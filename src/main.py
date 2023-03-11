
from bs4 import BeautifulSoup as bs
import datetime
from lxml import html
import os
import re
import requests
import time

# 九州商船のHP
KUSHO_DOMAIN = 'https://kyusho.co.jp'
KUSHO_SHIP_SCHEDULE = f'/publics/index/111/'

# 保存先
PAGE_SAVE_DIR = './save/html'


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


def get_page(page_url):
    """URLからページをダウンロードする
    - 最大で１日１回しか取得しないようにする
    - 取得時はこの関数内でsleepする

    Args:
        page_url (str): ダウンロードするページ
    Returns:
        パースされたlxmlオブジェクト
    """
    # urlが/で始まってたらフォルダとしてはトリム
    print(page_url)
    page_url_dir = page_url
    if (page_url_dir[0] == '/'):
        page_url_dir = page_url_dir[1:]

    # ローカルファイル用のフォルダ
    today = f'{datetime.date.today().year}{datetime.date.today().month}{datetime.date.today().day}'
    local_file_dir = os.path.join(os.getcwd(), PAGE_SAVE_DIR, page_url_dir)
    os.makedirs(local_file_dir, exist_ok=True)

    # ローカルファイル
    local_file_path = os.path.join(local_file_dir, f'{today}.html')

    # ファイルが存在していたらそれを読む、なければ取得する
    html_content = ''
    if (os.path.exists(local_file_path)):
        with open(local_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        print(f'Crawling... {KUSHO_DOMAIN}{page_url}')
        # ちょっと待つ（負荷をかけないように）
        time.sleep(1.5)

        # 取得
        r = requests.get(f'{KUSHO_DOMAIN}{page_url}')
        assert r.status_code == 200, 'response error!'

        sp = bs(r.content, 'html.parser')
        html_content = str(sp)

        # 保存
        with open(local_file_path, mode='w', encoding='utf-8') as f:
            f.write(html_content)

    # パース
    lxml_data = html.fromstring(html_content)

    return lxml_data


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
    # HTML取得
    lxml_data = get_page(page_info['url'])

    # //*[@id="block3813-9857"]/h3

    return []


if __name__ == '__main__':
    main()
