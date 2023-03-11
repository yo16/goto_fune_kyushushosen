"""toppage.py
トップページを読むための関数
"""
import re

from common import get_page

# トップページ
KUSHO_SHIP_SCHEDULE = f'/publics/index/111/'


def get_shipping_page_name_links() -> list:
    """右側のメニューから(航路名, 出航港, URL)のリストを返す
    """
    # 戻り値
    ret = []

    # HTMLを取得
    lxml_data = get_page(KUSHO_SHIP_SCHEDULE)

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
                'url': str(url)
            })

    return ret
