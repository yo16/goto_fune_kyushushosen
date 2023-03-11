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

            # スケジュールを読んで格納
            ret.append(schedule_info)

        elif (is_schedule_start_block(b)):
            # スケジュール開始ブロック
            start_schedule_block = True

            # スケジュール情報を読んで作成
            schedule_info = read_schedule_start_block(b)

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
    debug_parse_date_comment = True
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
    return []
