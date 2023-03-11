"""メイン
"""

from page_top import get_shipping_page_name_links
from page_sea_routes import get_schedule


def main():
    # 航路名、出航港、URLを取得
    pages = get_shipping_page_name_links()
    # print(pages)

    # ダイヤを取得
    schedules = []
    for p in pages:
        schedule_list = get_schedule(p)
        print(schedule_list)
        break   # for debug


if __name__ == '__main__':
    main()
