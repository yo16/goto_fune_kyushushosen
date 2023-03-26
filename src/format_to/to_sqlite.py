"""sqliteにする
"""
import os
import shutil
import sqlite3

from .common import get_today_str, PORTS


DB_NAME = 'goto_fune_sqlite.db'
TABLE_NAME = 'time_table'
COLUMN_DEFS = [
    {
        # 登録日
        'col_name': 'regist_ymd',
        'col_type': 'text'
    },
    {
        # 会社ID
        'col_name': 'ship_campany_id',
        'col_type': 'integer'
    },
    {
        # 船、ダイヤのタイトル
        'col_name': 'title',
        'col_type': 'text'
    },
    {
        # 船、ダイヤのサブタイトル
        'col_name': 'subtitle',
        'col_type': 'text'
    },
    {
        # 参考URL
        'col_name': 'url',
        'col_type': 'text'
    },
    {
        # 出発港ID
        'col_name': 'departure_port_id',
        'col_type': 'integer'
    },
    {
        # 出発港（文字列）
        'col_name': 'departure_port_name',
        'col_type': 'text'
    },
    {
        # 到着港ID
        'col_name': 'arrival_port_id',
        'col_type': 'integer'
    },
    {
        # 到着港（文字列）
        'col_name': 'arrival_port_name',
        'col_type': 'integer'
    },
    {
        # 時刻表の有効期間開始日
        'col_name': 'valid_period_from',
        'col_type': 'text'
    },
    {
        # 時刻表の有効期間終了日
        'col_name': 'valid_period_to',
        'col_type': 'text'
    },
    {
        # 出発時刻
        'col_name': 'departure_time',
        'col_type': 'text'
    },
    {
        # 到着時刻
        'col_name': 'arrival_time',
        'col_type': 'text'
    },
]

def to_sqlite(schedule_infos, output_dir='./output'):
    # コネクション取得（DB作成）
    conn = open_db(output_dir, recreate_table=True)

    # 接続切断
    conn.close()

    return


def open_db(output_dir, recreate_table=False, copy_todays_db=True):
    """DBを開く、ない場合は作成する
    ファイル名は固定でDB_NAME

    Args:
        output_dir (str): 出力先フォルダ
        recreate_table (bool): テーブルを再作成するかどうかのフラグ
        copy_todays_db (bool): 今日日付のファイルをcopyしておくフラグ
    """
    conn = None

    db_path = os.path.join(output_dir, DB_NAME)
    # ない場合は作成される
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 再作成
    if recreate_table:
        execute_query(cur, f'DROP TABLE IF EXISTS {TABLE_NAME};')
        sql = f'CREATE TABLE {TABLE_NAME} ('
        for i, c in enumerate(COLUMN_DEFS):
            if (i > 0):
                sql += ','
            sql += f'{c["col_name"]} {c["col_type"]}'
        sql += ');'
        execute_query(cur, sql)

    # 今日日付のファイルをコピーする
    if copy_todays_db:
        today_str = get_today_str()
        copy_db_name = f'{today_str}_{DB_NAME}'
        copy_db_path = os.path.join(output_dir, copy_db_name)

        # 存在する場合は上書きする
        shutil.copyfile(db_path, copy_db_path)

    return conn


def execute_query(cur, sql, debug_print=True):
    """SQLを実行する
    デバッグ用にプリントするかしないかを設定したいため、すべてここで実施

    Args:
        cur (object): カーソル
        sql (str): 実行するsql
        debug_print (bool): printするかしないかのフラグ
    """
    if debug_print:
        print(f'[SQL]:{sql}')
    
    cur.execute(sql)
