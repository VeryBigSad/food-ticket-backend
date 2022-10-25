import datetime

import qrcode


def get_qr_code_image(data: str):
    return qrcode.make(data)


def encode_data(expire_time: datetime.datetime, student_id: int):
    pass


def generate_qr(expire_time: datetime.datetime, student_id: int):
    pass



