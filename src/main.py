"""メイン
"""

from page_top import get_shipping_page_name_links
from page_sea_routes import get_sea_route_schedules
from format_to import format_to_goto_fune


def main():
    # 航路名、出航港、URLを取得
    pages = get_shipping_page_name_links()
    # print(pages)

    # ダイヤを取得
    schedules = []
    for p in pages:
        # if (p['url'] != '/publics/index/377/'):
        #    continue
        schedule_list = get_sea_route_schedules(p)
        schedules.extend(schedule_list)

    # print(schedules)
    format_to_goto_fune(schedules)


if __name__ == '__main__':
    main()
