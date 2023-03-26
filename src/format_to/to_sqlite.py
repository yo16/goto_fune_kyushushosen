"""sqliteにする
"""
import os
import shutil
import sqlite3

from .common import get_today_str, format_dtstr, map_name2id


DB_NAME = 'goto_fune_sqlite.db'
TABLE_NAME = 'time_table'
COLUMN_DEFS = [
    {
        # 登録日(YYYYMMDD)
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
        'col_type': 'text'
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
        # 出発時刻（hh:mm）
        'col_name': 'departure_time',
        'col_type': 'text'
    },
    {
        # 到着時刻（hh:mm）
        'col_name': 'arrival_time',
        'col_type': 'text'
    },
]


def to_sqlite(schedule_infos, output_dir='./output', copy_todays_db=True):
    """sqliteへ出力

    Args:
        schedule_infos (object): スケジュール情報
        output_dir (str, optional): 出力フォルダ. Defaults to './output'.
        copy_todays_db (bool, optional): 今日日付のdbを保存するフラグ. Defaults to True.
    """
    # コネクション取得（DB作成）
    db_path = os.path.join(output_dir, DB_NAME)
    conn = open_db(db_path, recreate_table=True)
    cur = conn.cursor()

    # insert
    recs = []
    ship_campany_id = 0
    today_str = get_today_str()
    for si in schedule_infos:
        title = si['schedule_name']
        subtitle = si['sub_title']
        url = si['url']

        for per in si['periods']:
            per_from_dt_str = format_dtstr(per['from'])
            per_to_dt_str = format_dtstr(per['to'])

            for pl in si['plans']:
                dep_port_name = pl['departure_port']
                arr_port_name = pl['arrival_port']
                dep_port_id = map_name2id(dep_port_name)
                arr_port_id = map_name2id(arr_port_name)
                
                for tm in pl['timetable']:
                    dep_tm = tm['departure_time']
                    arr_tm = tm['arrival_time']

                    # １レコード（注意：テーブルの列定義の順序と一致してる必要がある）
                    recs.append(
                        (
                            '"' + today_str + '"',
                            str(ship_campany_id),
                            '"' + title + '"',
                            '"' + subtitle + '"',
                            '"' + url + '"',
                            str(dep_port_id),
                            '"' + dep_port_name + '"',
                            str(arr_port_id),
                            '"' + arr_port_name + '"',
                            '"' + per_from_dt_str + '"',
                            '"' + per_to_dt_str + '"',
                            '"' + dep_tm + '"',
                            '"' + arr_tm + '"'
                        )
                    )
    # sqlを作成して実行
    sql = f'INSERT INTO {TABLE_NAME} VALUES '
    for i, rec in enumerate(recs):
        if (i > 0):
            sql += ','
        sql += '('
        sql += ','.join(rec)
        sql += ')'
    sql += ';'
    execute_query(cur, sql)

    # commit
    conn.commit()

    # 接続切断
    conn.close()

    # 今日日付のファイルをコピーする
    if copy_todays_db:
        copy_db_name = f'{today_str}_{DB_NAME}'
        copy_db_path = os.path.join(output_dir, copy_db_name)

        # 存在する場合は上書きする
        shutil.copyfile(db_path, copy_db_path)

    return


def open_db(db_path, recreate_table=False):
    """DBを開く、ない場合は作成する
    ファイル名は固定でDB_NAME

    Args:
        db_path (str): DBファイルパス
        recreate_table (bool): テーブルを再作成するかどうかのフラグ
    """
    conn = None

    # 接続する.存在しない場合は作成される
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

    return conn


def execute_query(cur, sql, debug_print=False):
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
