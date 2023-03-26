"""sqliteにする
"""
import os
import sqlite3


DB_NAME = 'goto_fune_sqlite.db'


def to_sqlite(schedule_infos, output_dir='./output'):
    # コネクション取得（DB作成）
    conn = open_db(output_dir)

    # 接続切断
    conn.close()

    return


def open_db(output_dir):
    """DBを開く、ない場合は作成する
    ファイル名は固定でDB_NAME

    Args:
        output_dir (str): 出力先フォルダ
    """
    conn = None

    db_path = os.path.join(output_dir, DB_NAME)
    # ない場合は作成される
    conn = sqlite3.connect(db_path)

    return conn
