import random
import string

import pandas as pd


def random_secret_code():
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for i in range(6)]
    )


def parse_excel_file(file):
    df = pd.read_excel(file)
    data_dict = df.to_dict()
    keys = data_dict.keys()
    fio_key = None
    fio_string = 'ФИО'
    grade_key = None
    grade_string = 'Класс (Группа)'
    status_key = None
    status_string = 'Статус'
    for key in keys:
        if fio_string in data_dict[key].values():
            fio_key = key
        elif grade_string in data_dict[key].values():
            grade_key = key
        elif status_string in data_dict[key].values():
            status_key = key
    data_dict[status_key] = {k: v for k, v in data_dict[status_key].items() if v == 'Подтвержден'}
    data_dict[fio_key] = {k: v for k, v in data_dict[fio_key].items() if k in data_dict[status_key].keys()}
    data_dict[grade_key] = {k: v for k, v in data_dict[grade_key].items() if k in data_dict[status_key].keys()}
    result = []
    for k, v in data_dict[fio_key].items():
        grade = ''.join(data_dict[grade_key][k].split('-'))
        result.append((v, grade))
    return result
