
import requests
from bs4 import BeautifulSoup as bs
from lxml import html
import re
import time

# 九州商船のHP
KUSHO_DOMAIN = 'https://kyusho.co.jp'
KUSHO_SHIP_SCHEDULE = f'{KUSHO_DOMAIN}/publics/index/111/'


def main():
    # 航路名、出航港、URLを取得
    pages = get_shipping_page_name_links()

    # ダイヤを取得
    schedules = []
    for p in pages:
        schedule_list = get_schedule(p)
        print(schedule_list)
        break   # for debug


def get_shipping_page_name_links() -> list:
    """右側のメニューから(航路名, 出航港, URL)のリストを返す
    """
    # 戻り値
    ret = []

    # HTML取得
    r = requests.get(KUSHO_SHIP_SCHEDULE)
    assert r.status_code == 200, 'response error!'

    # パース
    sp = bs(r.content, 'html.parser')
    lxml_data = html.fromstring(str(sp))

    # 航路
    sea_routes = lxml_data.xpath('//*[@id="parts12-center"]/nav/ul/li')
    for i, rt in enumerate(sea_routes):
        # 航路名
        # ブラウザで見ると先頭だけa/span/div/div だけど、
        # requestで取ると全部a/span
        sea_route_name = rt.xpath('a/span')[0].text
        #print(i, sea_route_name)

        # 出航港
        departures = rt.xpath('ul/li')
        for j, dp in enumerate(departures):
            departure_port_name = dp.xpath('a/span')[0].text
            # ｘｘ発だけにする
            if (not re.search('発\s*$', departure_port_name)):
                continue
            url = dp.xpath('a/@href')[0]
            #print(i, j, departure_port_name)

            ret.append({
                'sea_route': sea_route_name,
                'departures': departure_port_name,
                'url': url
            })

    return ret


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
    # ちょっと待つ（負荷をかけないように）
    time.sleep(1.5)

    # HTML取得
    r = requests.get(f'{KUSHO_DOMAIN}{page_info.url}')
    assert r.status_code == 200, 'response error!'

    # パース
    sp = bs(r.content, 'html.parser')
    lxml_data = html.fromstring(str(sp))

    # //*[@id="block3813-9857"]/h3

    return []


if __name__ == '__main__':
    main()
