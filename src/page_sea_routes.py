"""航路ごとのページを読む関数
"""
import datetime
from dateutil.relativedelta import relativedelta
import re

from common import get_page, get_full_url


def get_sea_route_schedules(page_info):
    """出航ダイヤを得る

    Args:
        page_info (object): {sea_route, departures, url}
    Returns: (list)
        [{
            schedule_name (str),
            periods (list): [{from, to}],
            plans (list): [{
                departure_port (str),
                arrival_port (str),
                timetable (list): [{
                    departure_time (str),
                    arrival_time (str)
                },]
            },],
            url(str)
        },]
    """
    ret = []

    # HTML取得
    lxml_data = get_page(page_info['url'])

    # block-listsのdivを順番に見る
    div_blocks = lxml_data.xpath('//*[@id="block-lists"]/div')
    start_schedule_block = False
    got_period_info = False
    write_period_next = False
    schedule_info = {}
    for b in div_blocks:
        # スケジュール開始ブロックかどうか判定し、
        # スケジュール開始ブロックの場合はその情報を読むとともに
        # つぎのブロックがスケジュールブロックであるフラグを立てる
        # スケジュールブロックの場合は、スケジュールを読む
        if (start_schedule_block):
            # 前のブロックが、スケジュール開始ブロックだったので
            # このブロックは、スケジュールブロック
            start_schedule_block = False

            print(schedule_info["schedule_name"])
            # スケジュールを読む
            plans = read_schedule_block(b)
            # periodも取ってないしスケジュールも取れなかった場合
            if ((not got_period_info) and (len(plans) == 0)):
                # 全便休航ということがこのブロックに書いてある
                # (本来はスケジュール開始ブロックに書かれるはずの)日付も
                # ここに書いてしまっている
                # なので今のブロックをスケジュール開始ブロックとみなして
                # スケジュール情報を読む
                schedule_info_illegular, got_period_info_illegular = read_schedule_start_block(
                    b)
                # ここで得たperiodsを、カレントのschedule_infoに設定
                schedule_info['periods'] = schedule_info_illegular['periods']
                # その場合plansは空だが、休航なので問題なし
                # さらにこの後の処理で、ドック期間を除く処理が走る
            print('ぷらんず')
            print(plans)
            schedule_info['plans'] = plans

            # 結果オブジェクトに設定
            ret.append(schedule_info)

            # 次に書くフラグが立っている場合、今のブロックの情報をもとに、
            # １つ前の情報を書き換える
            if (write_period_next):
                period_info = calc_period_from_prev_schedule_info(
                    ret[len(ret)-1]     # 元となる、今の情報
                )
                print(period_info)
                ret[len(ret)-2]['periods'] = period_info

                write_period_next = False

            # 追加した情報に、periodがない場合、次のブロックから算出するため、
            # 次に書くフラグを立てておく
            if (not got_period_info):
                write_period_next = True
            got_period_info = False

        elif (is_schedule_start_block(b)):
            # スケジュール開始ブロック
            start_schedule_block = True

            # スケジュール情報を読んで作成
            schedule_info, got_period_info = read_schedule_start_block(b)

            # ついでにURLも書いておく
            schedule_info['url'] = get_full_url(page_info['url'])

    # test_print_schedule_info(ret)
    return ret


def is_schedule_start_block(block):
    """ブロック(div要素)がスケジュールのダイヤ名が入っているブロックかどうかを判定

    Args:
        block (object): lxmlオブジェクトのdiv要素
    Returns:
        True: スケジュール開始ブロック
        False: スケジュール開始ブロックではない
    """
    title_elm = block.xpath('div/div/div/h3/span[@class="vi-direct-item"]')
    if (len(title_elm) == 0):
        return False

    return True


def read_schedule_start_block(block):
    """スケジュール開始ブロックを読む

    Args:
        block (object): lxmlオブジェクトのdiv要素
    Returns:
        schedule_info (object): {
            schedule_name (str),
            periods (list): [{from, to}]
        },
        True: 時刻を取得できた | False:取得できなかった
    """
    # スケジュール名
    title_elms = block.xpath('div/div/div/h3/span[@class="vi-direct-item"]')
    if (len(title_elms) > 0):
        schedule_name = title_elms[0].text
    else:
        schedule_name = ''

    # コメント
    comment = ''
    comment_elms = block.xpath('div/div/div/div/div/div')
    if (len(comment_elms) > 0):  # ないときがある！
        comment_elm = block.xpath('div/div/div/div/div/div')[0]
        comment = comment_elm.text

    periods = parse_date_comment(comment)

    return {'schedule_name': schedule_name, 'periods': periods}, (len(periods) > 0)


def parse_date_comment(c):
    """スケジュールが適用される日付の文字列を読み解いて、from/toの組み合わせにする
    cが空の場合は空を返す

    Args:
        c (str): 日付が部分
    Returns:
        periods (list): [
            {from, to}
        ]
    """
    debug_parse_date_comment = True
    ret = []
    if (debug_parse_date_comment):
        print('parse_date_comment start')
        print(c)

    # 何も書いていないときや、本当にコメントしか書いていないときはスキップ
    if (len(c) == 0):
        return ret
    if (not re.search(r'\d', c)):   # 数字が入っていない
        return ret

    year = datetime.date.today().year
    month = datetime.date.today().month

    # "、"でsplit
    words = re.split(r'、\s*', c)
    for w in words:
        cur_w = w
        # スペースをトリム
        cur_w = cur_w.strip()
        if (debug_parse_date_comment):
            print(f'cur_w:{cur_w}')

        # "～"で日付が範囲指定されているパターン
        m_kara = re.search(r'^(.+)～(.+)', cur_w)
        if (m_kara):
            if (debug_parse_date_comment):
                print('kara')
            ymds = []   # fromとto
            for s in m_kara.groups():
                # YMDをパース
                year, month, day = parse_ymd(s, year, month)

                # １つ追加
                ymds.append(f'{year}/{month}/{day}')

            # ２つそろったらfrom/to
            current_from_to = {'from': ymds[0], 'to': ymds[1]}
            if (debug_parse_date_comment):
                print(current_from_to)
            ret.append(current_from_to)

        else:
            # "・"で複数指定されているパターン
            m_dot = re.search(r'^(.+)・(.+)', cur_w)
            if (m_dot):
                if (debug_parse_date_comment):
                    print('dot')
                # "・"でsplit
                for s in re.split(r'・', cur_w):
                    # YMDをパース
                    year, month, day = parse_ymd(s, year, month)

                    # １つでfrom/to
                    ymd_str = f'{year}/{month}/{day}'
                    current_from_to = {'from': ymd_str, 'to': ymd_str}
                    if (debug_parse_date_comment):
                        print(current_from_to)
                    ret.append(current_from_to)

            else:
                if (debug_parse_date_comment):
                    print('single')
                # それ以外（～も・もない）
                year, month, day = parse_ymd(cur_w, year, month)

                # １つでfrom/to
                ymd_str = f'{year}/{month}/{day}'
                current_from_to = {'from': ymd_str, 'to': ymd_str}
                if (debug_parse_date_comment):
                    print(current_from_to)
                ret.append(current_from_to)

    if (debug_parse_date_comment):
        print('parse_date_comment end')

    return ret


def parse_ymd(s, year, month):
    """ymdの部分をparseする

    Args:
        s (string): 年月日の文字列
    """
    # 先頭に数字が4つあったら年を更新
    m = re.search(r'^((\d{4})．)(.*)', s)
    y_str = ''
    md_str = s
    if (m):
        # 年のパートがある
        y_str = m.groups()[1]
        year = int(y_str)
        # 月日は、年を除外した部分
        md_str = m.groups()[2]

    # "／"があったら月と日
    m = re.search(r'^(\d+)[／/]((\d+)|末)', md_str)  # 最後に"（予定）"とかがあるときがある
    d_str = md_str
    if (m):
        # 月のパートがあったら月を更新
        m_str = m.groups()[0]
        if (m.groups()[1] == '末'):
            # 翌月の1日から1日引く=今月の月末
            dt = datetime.date(year, int(m_str), 1) + \
                relativedelta(months=+1, day=1, days=-1)
            # 無駄だけど普通のケースに合わせてstrにしておく
            d_str = str(dt.day)
        else:
            d_str = m.groups()[1]
        month = int(m_str)

    # d_strに数値以外があったら除外
    m = re.search(r'\d+', d_str)
    assert m, 'Not contain an integer'
    d_str = m.group()

    # 日
    day = int(d_str)

    return (year, month, day)


def read_schedule_block(block):
    """スケジュールブロックを読む

    Args:
        block (object): lxmlオブジェクトのdiv要素
    Returns:
        plans (list): [{
                departure_port (str),
                arrival_port (str),
                timetable (list): [{
                    departure_time (str),
                    arrival_time (str)
                },]
            },]
    """
    debug_read_schedule_block1 = True
    if debug_read_schedule_block1:
        print('read_schedule_block')

    ret = []
    ports_list = []
    time_list = None

    # trを取得
    trs = block.xpath('div/div/div/div/table/tbody/tr')
    # 読み取り
    for i, tr in enumerate(trs):
        # tdを取得
        tds = tr.xpath('td')
        if debug_read_schedule_block1:
            print(i)

        # tdの数を使って、time_listの箱だけ作る
        if (i == 0):
            time_list = [[] for _ in range(len(tds)-2)]

        for j, td in enumerate(tds):
            if debug_read_schedule_block1:
                print(i, j)
            # テキストを抽出
            cur_text = ""       # 一致するものがないときは空
            xpath_list = ['div/span/span', 'div/span', 'div']
            for p in xpath_list:
                cell_div = td.xpath(p)
                if (len(cell_div) > 0):
                    # 見つけた
                    cur_text = cell_div[0].text
                    break

            # １列目は港名
            if (j == 0):
                # たまに間違って、"着"か"発"が書いてあるから削除
                if (re.search(f'.*[発着]$', cur_text)):
                    cur_text = cur_text[:-1]
                ports_list.append(cur_text)
            # ２列目は発着（使わない）
            # ３列目以降が時刻
            if (j >= 2):
                time_str = None
                # 時刻フォーマットのみ
                m = re.search(r'\d+:\d+', cur_text)
                if (m):
                    time_str = m.group()
                time_list[j-2].append(time_str)
    # print(ports_list)
    # print(time_list)

    dpt_arvs = {}
    # 港のfrom-toの組み合わせで時刻を設定
    for i, dpt in enumerate(ports_list[:-1]):
        for j_1, arv in enumerate(ports_list[i+1:]):
            # enumerateの結果はそのままではports_listに使えないので注意
            j = i + j_1 + 1
            # time_listは、表の１日の本数と一致する
            for k, tm in enumerate(time_list):    # １本ごとの処理にする
                if ((tm[i] is not None) and (tm[j] is not None)):
                    if (dpt not in dpt_arvs.keys()):
                        dpt_arvs[dpt] = {}
                    if (arv not in dpt_arvs[dpt].keys()):
                        dpt_arvs[dpt][arv] = []

                    dpt_arvs[dpt][arv].append({
                        'departure_time': tm[i],
                        'arrival_time': tm[j]
                    })
    # print(dpt_arvs)

    # 戻り値に移し替え
    for k_dpt, v_dpt in dpt_arvs.items():
        for k_arv, v_arv in v_dpt.items():
            ret.append({
                'departure_port': k_dpt,
                'arrival_port': k_arv,
                'timetable': v_arv
            })
    # print(ret)

    return ret


def calc_period_from_prev_schedule_info(refered_schedule_info):
    """参考とするスケジュール情報をもとに、スケジュール情報を作成して返す
    具体的には、参考とするスケジュール情報でない日を、設定する

    Args:
        refered_schedule_info (object): 参考とするスケジュール情報
    """
    new_periods = []

    # 今年
    this_year = datetime.date.today().year
    # 翌年
    next_year = this_year + 1

    # 開始日
    start_dt_str = f'{this_year}/1/1'
    start_dt = datetime.datetime.strptime(start_dt_str, '%Y/%m/%d')
    # 終了日
    end_dt_str = f'{next_year}/12/31'
    end_dt = datetime.datetime.strptime(end_dt_str, '%Y/%m/%d')

    # 今年の1/1から12/31の範囲で、refered_schedule_info.
    for p in refered_schedule_info['periods']:
        # 参考のfrom/to
        period_from = p['from']
        period_to = p['to']
        period_from_dt = datetime.datetime.strptime(
            period_from, '%Y/%m/%d')
        period_to_dt = datetime.datetime.strptime(
            period_to, '%Y/%m/%d')

        # fromの前日
        period_from_dt_pre = period_from_dt - datetime.timedelta(1)
        # toの翌日
        period_to_dt_next = period_to_dt + datetime.timedelta(1)

        # もしfromの前日(toになる)が、end_dtより先の場合は、
        # end_dtを最終日にする
        if (end_dt < period_from_dt_pre):
            period_from_dt_pre = end_dt

        # 追加
        new_periods.append({
            'from': start_dt.strftime('%Y/%m/%d'),
            'to': period_from_dt_pre.strftime('%Y/%m/%d')
        })

        # 次のためのstart_dtを更新
        # toの翌日か、end_dtの小さいほう
        if (period_to_dt_next < end_dt):
            # 普通はこちら
            start_dt = period_to_dt_next
        else:
            # periodの日付がおかしかったり、end_dtが短い場合にこれになりうる
            start_dt = end_dt

    # 最後のfromとto
    # start_dtから、end_dtまで
    new_periods.append({
        'from': start_dt.strftime('%Y/%m/%d'),
        'to': end_dt.strftime('%Y/%m/%d')
    })

    # 対象を返す
    return new_periods


def test_print_schedule_info(schedule_infos):
    """schedule_infoを正しく読めているか、確認するための関数

    Args:
        schedule_infos (object): 読み込んだschedule_infoオブジェクト
    """
    for si in schedule_infos:
        sche_name = si['schedule_name']
        print(f'■{sche_name}')

        print('periods')
        for p in si['periods']:
            from_dt = p['from']
            to_dt = p['to']
            print(f'  - {from_dt} -> {to_dt}')

        print('time_table')
        for p in si['plans']:
            departure_port = p['departure_port']
            arrival_port = p['arrival_port']
            print(f' - {departure_port} -> {arrival_port}')
            for tm in p['timetable']:
                tm_from = tm['departure_time']
                tm_to = tm['arrival_time']
                print(f'    + {tm_from} -> {tm_to}')
