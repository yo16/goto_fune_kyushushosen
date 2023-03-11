"""共通関数
"""
from bs4 import BeautifulSoup as bs
import datetime
from lxml import html
import os
import requests
import time

# 九州商船のHP
KUSHO_DOMAIN = 'https://kyusho.co.jp'

# 保存先
PAGE_SAVE_DIR = './save/html'


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
    today = get_today_str()
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
        full_url = get_full_url(page_url)
        print(f'Crawling... {full_url}')
        # ちょっと待つ（負荷をかけないように）
        time.sleep(1.5)

        # 取得
        r = requests.get(f'{full_url}')
        assert r.status_code == 200, 'response error!'

        sp = bs(r.content, 'html.parser')
        html_content = str(sp)

        # 保存
        with open(local_file_path, mode='w', encoding='utf-8') as f:
            f.write(html_content)

    # パース
    lxml_data = html.fromstring(html_content)

    return lxml_data


def get_full_url(url):
    return f'{KUSHO_DOMAIN}{url}'


def get_today_str():
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    return f'{year}{month:02}{day:02}'


if __name__ == '__main__':
    print(get_today_str())
