import datetime
import json
import os

from common import get_today_str

# goto_funeで定義されている港のid
PORTS = [
    {'id': 0,  'name': '長崎',    'group': 9},   {'id': 1,  'name': '奈良尾',  'group': 0},   {'id': 2,  'name': '福江',    'group': 1},   {'id': 3,  'name': '奈留島',  'group': 2},   {'id': 4,  'name': '有川',    'group': 0},   {'id': 5,  'name': '佐世保',  'group': 9},   {'id': 6,  'name': '小値賀',  'group': 2},   {'id': 7,  'name': '宇久平',  'group': 2},   {'id': 8,  'name': '博多',    'group': 9},   {'id': 10, 'name': '青方',    'group': 0},   {'id': 11, 'name': '奥浦',    'group': 1},   {'id': 12, 'name': '田ノ浦',  'group': 2},   {
        'id': 13, 'name': '本窯',    'group': 2},   {'id': 14, 'name': '伊福貴',  'group': 2},   {'id': 15, 'name': '嵯峨島',  'group': 2},   {'id': 16, 'name': '貝津',    'group': 1},   {'id': 17, 'name': '赤島',    'group': 2},   {'id': 18, 'name': '黄島',    'group': 2},   {'id': 19, 'name': '石松',    'group': 2},   {'id': 20, 'name': '土井浦',  'group': 2},   {'id': 21, 'name': '郷ノ首',  'group': 0},   {'id': 22, 'name': '若松',    'group': 2},   {'id': 23, 'name': '前島',    'group': 2},   {'id': 24, 'name': '笠松',    'group': 2}
]


def format_to_goto_fune(schedule_infos, output_dir='./output'):
    """goto_funeのtimetables.jsに書くためのフォーマットに変換
    goto_fune
        https://github.com/yo16/goto_fune

    Args:
        schedule_infos (list): スケジュール情報
    """
    # 出力先
    today_str = get_today_str()
    file_name = f'{today_str}.json'

    ret = {
        'ship_campany': 0,
        'ships': []
    }

    # 港の名前→idの対応表を作成
    map_name2id = {p['name']: p['id'] for p in PORTS}

    for si in schedule_infos:
        sche_name = si['schedule_name']
        print(f'schedule_name:{sche_name}')
        url = si['url']

        ship_info = {
            'title': sche_name,
            'timetable_url': url,
            'periods': []
        }

        for p in si['periods']:
            from_dt = p['from']
            to_dt = p['to']
            ship_info['periods'].append({
                'from': from_dt,
                'to': to_dt
            })

        plans = []
        for p in si['plans']:
            departure_port = map_name2id[p['departure_port']]
            arrival_port = map_name2id[p['arrival_port']]
            plan = {
                'from': departure_port,
                'to': arrival_port,
                'timetable': []
            }
            for tm in p['timetable']:
                tm_from = tm['departure_time']
                tm_to = tm['arrival_time']
                plan['timetable'].append({
                    'departure': tm_from,
                    'arrival': tm_to
                })
            plans.append(plan)
        ship_info['plans'] = plans

        ret['ships'].append(ship_info)

    # 出力
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, file_name)
    with open(output_file_path, mode='w', encoding='utf-8') as f:
        json.dump(ret, f, indent=4, ensure_ascii=False)
