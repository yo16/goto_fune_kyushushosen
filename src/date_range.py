"""日付範囲の集合を計算する
"""
from datetime import datetime, timedelta


def dates_subtract(base_list, substract_list):
    """baseからsubstractを除外する
    base、substractともに同じ形式のオブジェクトのリスト。
    オブジェクトは、
    {
        'from': 'yyyy/mm/dd'(str),
        'to': 'yyyy/mm/dd'(str)
    }
    の形式。
    戻り値も同じ形式のオブジェクトのリストを返す。

    Args:
        base_list (list): 引かれる元の範囲
        substract_list (list): 除外する範囲
    Returns:
        (list): baseからsubstractを除外した範囲
    """
    debug_dates_subtract = False
    ret = []

    base_itr = dt_iterator(base_list)
    sub_itr = dt_iterator(substract_list)

    try:
        cur_base = None
        cur_base = base_itr.__next__()
        cur_sub = None
        cur_sub = sub_itr.__next__()
    except StopIteration:
        if cur_base:
            # baseはあるが、subは空
            ret.append(get_dt_obj(cur_base[0], cur_base[1]))
            for cur_base in base_itr:
                ret.append(get_dt_obj(cur_base[0], cur_base[1]))
            return ret
        else:
            # subはあるが、baseは空
            return []

    if debug_dates_subtract:
        print('dates_subtract')
        print(base_list)
        print(substract_list)

    try:
        while(True):
            if debug_dates_subtract:
                print('-----')
                print(cur_base)
                print(cur_sub)
            # 1. 開始時の関係
            if (cur_base[0] < cur_sub[0]):
                # baseの方が早い場合は、retに追加される期間が生じる
                # → 追加される期間を特定する
                if debug_dates_subtract:
                    print('開始-A')

                # 2. 終了時の関係
                if (cur_sub[0] <= cur_base[1]):
                    # subが先に終わる、または同じ場合は、subの開始の前の日までを追加
                    if debug_dates_subtract:
                        print('終了-A')
                    ret.append(get_dt_obj(cur_base[0], day_before(cur_sub[0])))

                    if (cur_sub[0] == cur_base[1]):
                        # 同じ場合は、baseは新しいものにする
                        cur_base = None
                        cur_base = base_itr.__next__()
                    else:
                        # 同じでない（baseがまだ続く）場合は、
                        # 今のbaseのfromをcur_subのtoの翌日にする
                        # ただしbaseもcur_subのtoまでには終わる場合は、baseを新しいものにする
                        if (cur_base[1] <= cur_sub[1]):
                            # baseが、subの開始時にはまだ続いていたが、subの終了時までは続かなかった
                            cur_base = None
                            cur_base = base_itr.__next__()
                        else:
                            # baseが、subの終了後も続いている
                            cur_base[0] = day_after(cur_sub[1])

                else:
                    # baseが先に終わる場合は、baseの期間を追加
                    if debug_dates_subtract:
                        print('終了-B')
                    ret.append(get_dt_obj(cur_base[0], cur_base[1]))

                    # baseの次を取得
                    cur_base = None
                    cur_base = base_itr.__next__()

            else:
                # subの方が早いか同じ場合は、retに追加されない
                # → 追加されない期間を特定する
                if debug_dates_subtract:
                    print('開始-B')

                # 2. 終了時の関係
                if (cur_base[1] <= cur_sub[1]):
                    # baseの方が先に終わる、または同じ場合
                    if debug_dates_subtract:
                        print('終了-A')
                    if (cur_base[1] == cur_sub[1]):
                        if debug_dates_subtract:
                            print('終了も一致')
                        # 同じ場合は、先にbaseを取得してから、次のsubを取得
                        # exceptionに入ったとき、baseがあるとレコードを作ってしまうため
                        cur_base = None
                        cur_base = base_itr.__next__()

                        cur_sub = None
                        cur_sub = sub_itr.__next__()

                    else:
                        # 同じでない（subがまだ続く）場合は
                        # subのfromをbaseのtoの翌日にしてから、次のbaseを取得
                        cur_sub[0] = day_after(cur_base[1])

                        # 次のbaseを取得
                        cur_base = None
                        cur_base = base_itr.__next__()

                else:
                    # subの方が先に終わる場合は、baseのformをsubのtoの翌日にする
                    if debug_dates_subtract:
                        print('終了-B')
                    cur_base[0] = day_after(cur_sub[1])

                    # 次のsubを取得
                    cur_sub = None
                    cur_sub = sub_itr.__next__()

    except StopIteration:
        if cur_base:
            # baseがあるということは、subが先になくなったので
            # baseのfrom-toをretに追加
            ret.append(get_dt_obj(cur_base[0], cur_base[1]))

    return ret


def dt_iterator(dt_list):
    """日付のオブジェクトをリストにして返す
    ついでに文字列のdtを日付型にする

    Args:
        dt_list (object): from, toを持つオブジェクト

    Yields:
        (list): 日付型のfrom,toのリスト
    """
    for dt in dt_list:
        yield [
            str_to_dt(dt['from']),
            str_to_dt(dt['to'])
        ]


def get_dt_obj(dt_from, dt_to):
    return {
        'from': dt_to_str(dt_from),
        'to': dt_to_str(dt_to)
    }


def day_before(dt):
    # dtの前日を返す
    return dt - timedelta(days=1)


def day_after(dt):
    # dtの翌日を返す
    return dt + timedelta(days=1)


def str_to_dt(s):
    return datetime.strptime(s, '%Y/%m/%d')


def dt_to_str(dt):
    return dt.strftime('%Y/%m/%d')


def test_dates_subtract(test_base, test_sub, expects):
    ret_lists = dates_subtract(
        test_base, test_sub
    )
    print('** return')
    print(ret_lists)
    assert len(ret_lists) == len(expects)
    for i, dt_range in enumerate(ret_lists):
        assert str_to_dt(dt_range['from']) == str_to_dt(expects[i][0])
        assert str_to_dt(dt_range['to']) == str_to_dt(expects[i][1])

    print('** ok!')


if __name__ == '__main__':
    print('test A-A')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/5/30'}],
        [{'from': '2023/3/1', 'to': '2023/3/31'}],
        [('2023/1/1', '2023/2/28'), ('2023/4/1', '2023/5/30')]
    )

    print('test A-AB')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/5/30'}],
        [{'from': '2023/3/10', 'to': '2023/5/30'}],
        [('2023/1/1', '2023/3/9')]
    )

    print('test A-B')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/5/30'}],
        [{'from': '2023/3/10', 'to': '2023/6/10'}],
        [('2023/1/1', '2023/3/9')]
    )

    print('test AB-A')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/5/31'}],
        [{'from': '2023/1/1', 'to': '2023/4/10'}],
        [('2023/4/11', '2023/5/31')]
    )

    print('test AB-AB')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/5/31'}],
        [{'from': '2023/1/1', 'to': '2023/5/31'}],
        []
    )

    print('test AB-B')
    test_dates_subtract(
        [{'from': '2023/1/1', 'to': '2023/3/10'}],
        [{'from': '2023/1/1', 'to': '2023/5/31'}],
        []
    )

    print('test B-A')
    test_dates_subtract(
        [{'from': '2023/2/1', 'to': '2023/5/10'}],
        [{'from': '2023/1/1', 'to': '2023/3/31'}],
        [('2023/4/1', '2023/5/10')]
    )

    print('test B-AB')
    test_dates_subtract(
        [{'from': '2023/2/1', 'to': '2023/5/10'}],
        [{'from': '2023/1/1', 'to': '2023/5/10'}],
        []
    )

    print('test B-B')
    test_dates_subtract(
        [{'from': '2023/2/1', 'to': '2023/3/10'}],
        [{'from': '2023/1/1', 'to': '2023/5/10'}],
        []
    )

    print('test case1')
    test_dates_subtract(
        [
            {'from': '2023/1/1', 'to': '2023/12/31'},
        ],
        [
            {'from': '2023/2/1', 'to': '2023/3/31'},
            {'from': '2023/5/1', 'to': '2023/7/31'}
        ],
        [
            ('2023/1/1', '2023/1/31'),
            ('2023/4/1', '2023/4/30'),
            ('2023/8/1', '2023/12/31')
        ]
    )

    print('test case2')
    test_dates_subtract(
        [
            {'from': '2023/1/1', 'to': '2023/2/10'},
            {'from': '2023/3/1', 'to': '2023/3/10'},
            {'from': '2023/5/1', 'to': '2023/12/31'},
        ],
        [
            {'from': '2023/2/1', 'to': '2023/7/1'}
        ],
        [
            ('2023/1/1', '2023/1/31'),
            ('2023/7/2', '2023/12/31')
        ]
    )

    print('test case3')
    test_dates_subtract(
        [
            {'from': '2023/1/1', 'to': '2023/11/10'}
        ],
        [
            {'from': '2023/2/1', 'to': '2023/2/10'},
            {'from': '2023/4/1', 'to': '2023/4/10'},
            {'from': '2023/11/1', 'to': '2023/12/31'},
        ],
        [
            ('2023/1/1', '2023/1/31'),
            ('2023/2/11', '2023/3/31'),
            ('2023/4/11', '2023/10/31')
        ]
    )

    print('test case4')
    test_dates_subtract(
        [],
        [
            {'from': '2023/1/1', 'to': '2023/11/10'}
        ],
        []
    )

    print('test case5')
    test_dates_subtract(
        [
            {'from': '2023/1/1', 'to': '2023/11/10'}
        ],
        [],
        [
            ('2023/1/1', '2023/11/10')
        ]
    )

    print('test case6')
    test_dates_subtract(
        [],
        [],
        []
    )
