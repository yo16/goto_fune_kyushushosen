
import datetime


# goto_funeで定義されている港のid
PORTS = [
    {'id': 0,  'name': '長崎',    'group': 9},   {'id': 1,  'name': '奈良尾',  'group': 0},   {'id': 2,  'name': '福江',    'group': 1},   {'id': 3,  'name': '奈留島',  'group': 2},   {'id': 4,  'name': '有川',    'group': 0},   {'id': 5,  'name': '佐世保',  'group': 9},   {'id': 6,  'name': '小値賀',  'group': 2},   {'id': 7,  'name': '宇久平',  'group': 2},   {'id': 8,  'name': '博多',    'group': 9},   {'id': 10, 'name': '青方',    'group': 0},   {'id': 11, 'name': '奥浦',    'group': 1},   {'id': 12, 'name': '田ノ浦',  'group': 2},   {
        'id': 13, 'name': '本窯',    'group': 2},   {'id': 14, 'name': '伊福貴',  'group': 2},   {'id': 15, 'name': '嵯峨島',  'group': 2},   {'id': 16, 'name': '貝津',    'group': 1},   {'id': 17, 'name': '赤島',    'group': 2},   {'id': 18, 'name': '黄島',    'group': 2},   {'id': 19, 'name': '石松',    'group': 2},   {'id': 20, 'name': '土井浦',  'group': 2},   {'id': 21, 'name': '郷ノ首',  'group': 0},   {'id': 22, 'name': '若松',    'group': 2},   {'id': 23, 'name': '前島',    'group': 2},   {'id': 24, 'name': '笠松',    'group': 2}
]

# 港の名前→idの対応表
_map_name2id = {p['name']: p['id'] for p in PORTS}
def map_name2id(port_name):
    return _map_name2id[port_name]


def get_today_str():
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    return f'{year}{month:02}{day:02}'


def format_dtstr(str_sepalated, sepalate_str='/'):
    """スラッシュで区切られた文字列をYYYYMMDD形式にする

    Args:
        str_sepalated (str): 変更前の文字列
        sepalate_str (str, optional): YYYYMMDD8文字の文字列. Defaults to '/'.
    """
    # まずdate型にする
    ymd_parts = str_sepalated.split(sepalate_str)
    assert(len(ymd_parts)==3, ymd_parts)
    cur_date = datetime.date(int(ymd_parts[0]), int(ymd_parts[1]), int(ymd_parts[2]))

    # フォーマットして返す
    return f'{cur_date.year}{cur_date.month:02}{cur_date.day:02}'
