"""航路ごとのページを読む関数
"""
import datetime
import re

from common import get_page


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
            },]
        },]
    """
    ret = []

    # HTML取得
    lxml_data = get_page(page_info['url'])

    # block-listsのdivを順番に見る
    div_blocks = lxml_data.xpath('//*[@id="block-lists"]/div')
    start_schedule_block = False
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

            # print(schedule_info["schedule_name"])
            # スケジュールを読む
            schedule_info['plans'] = read_schedule_block(b)

            # 結果オブジェクトに設定
            ret.append(schedule_info)

        elif (is_schedule_start_block(b)):
            # スケジュール開始ブロック
            start_schedule_block = True

            # スケジュール情報を読んで作成
            schedule_info = read_schedule_start_block(b)

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
        }
    """
    title_elm = block.xpath('div/div/div/h3/span[@class="vi-direct-item"]')[0]
    comment_elm = block.xpath('div/div/div/div/div/div')[0]

    # スケジュール名
    schedule_name = title_elm.text

    # コメント
    comment = comment_elm.text
    periods = parse_date_comment(comment)

    return {'schedule_name': schedule_name, 'periods': periods}


def parse_date_comment(c):
    """スケジュールが適用される日付の文字列を読み解いて、from/toの組み合わせにする

    Args:
        c (str): 日付が部分
    Returns:
        periods (list): [
            {from, to}
        ]
    """
    debug_parse_date_comment = False
    ret = []
    if (debug_parse_date_comment):
        print(c)

    year = datetime.date.today().year
    month = datetime.date.today().month

    # "、"でsplit
    words = re.split(r'、\s*', c)
    for w in words:
        cur_w = w
        # スペースをトリム
        cur_w = cur_w.strip()

        # "～"で日付が範囲指定されているパターン
        m_kara = re.search(r'^(.+)～(.+)', cur_w)
        if (m_kara):
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
                # それ以外（～も・もない）
                year, month, day = parse_ymd(cur_w, year, month)

                # １つでfrom/to
                ymd_str = f'{year}/{month}/{day}'
                current_from_to = {'from': ymd_str, 'to': ymd_str}
                if (debug_parse_date_comment):
                    print(current_from_to)
                ret.append(current_from_to)

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
    m = re.search(r'^(\d+)[／/](\d+)$', md_str)
    d_str = md_str
    if (m):
        # 月のパートがあったら月を更新
        m_str = m.groups()[0]
        d_str = m.groups()[1]
        month = int(m_str)

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
    ret = []
    ports_list = []
    time_list = None

    # trを取得
    trs = block.xpath('div/div/div/div/table/tbody/tr')
    # 読み取り
    for i, tr in enumerate(trs):
        # tdを取得
        tds = tr.xpath('td')

        # tdの数を使って、time_listの箱だけ作る
        if (i == 0):
            time_list = [[] for _ in range(len(tds)-2)]

        for j, td in enumerate(tds):
            # テキストを抽出
            cur_text = ""       # 一致するものがないときは空
            cell_div = td.xpath('div/span')  # spanがあるときとないときがある
            if (len(cell_div) == 0):
                cell_div = td.xpath('div')
                if (len(cell_div) > 0):
                    cur_text = cell_div[0].text
            else:
                cur_text = cell_div[0].text

            # １列目は港名
            if (j == 0):
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


def test_print_schedule_info(schedule_infos):
    """schedule_infoを正しく読めているか、確認するための関数

    Args:
        schedule_infos (object): 読み込んだschedule_infoオブジェクト
    """
    for si in schedule_infos:
        sche_name = si['schedule_name']
        print(f'■{sche_name}')

        print('period')
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
