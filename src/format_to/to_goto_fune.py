import json
import os

from .common import get_today_str, map_name2id


def to_goto_fune(schedule_infos, output_dir='./output'):
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

    for si in schedule_infos:
        sche_name = si['schedule_name']
        print(f'schedule_name:{sche_name}')
        sub_title = si['sub_title']
        url = si['url']

        ship_info = {
            'title': sche_name,
            'sub_title': sub_title,
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
                'from_str': p['departure_port'],
                'to': arrival_port,
                'to_str': p['arrival_port'],
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
