"""航路ごとのページを読む関数
"""

from common import get_page


def get_schedule(page_info):
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
    print('判定！')

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
    schedule_name = ''
    periods = []

    return {'schedule_name': schedule_name, 'periods': periods}


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
