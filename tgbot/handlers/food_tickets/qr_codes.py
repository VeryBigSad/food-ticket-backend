import datetime
import json

import rc4
import qrcode


def get_qr_code_image(data: str):
    return qrcode.make(data)


def encode_data(expire_time: datetime.datetime, student_id: int):
    data = {
        'expire': expire_time.strftime('%d.%m %H:%M:%S'),
        'id': student_id
    }

    data = json.dumps(data)
    encoded = rc4.rc4(data, 'МММБОЖЕ8КЛАССНИЦЫТАКИЕСОСОЧКИМММИФКНТОПКСТА')
    return encoded


def generate_qr(expire_time: datetime.datetime, student_id: int):
    pass



