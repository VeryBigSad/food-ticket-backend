from io import BytesIO
import rc4
import json
import qrcode
import datetime
from PIL import Image
from tgbot.settings import ENCRYPTION_KEY


def get_qr_code_image(data: str) -> Image:
    return qrcode.make(f"@school58bot{data}")


def encode_data(expire_time: datetime.datetime, student_id: int) -> str:
    data = {"expire": expire_time.strftime("%d.%m %H:%M:%S"), "id": student_id}

    data = json.dumps(data)

    encoded = rc4.rc4(data, ENCRYPTION_KEY)
    return encoded


def save_image(image: Image, filename="image") -> BytesIO:
    bytes = BytesIO()
    bytes.name = f"{filename}.jpeg"

    image.save(bytes, "JPEG")
    bytes.seek(0)
    return bytes


def generate_qr(expire_time: datetime.datetime, student_id: int) -> Image:
    encrypted = encode_data(expire_time, student_id)

    qr_image = get_qr_code_image(encrypted)
    qr = save_image(qr_image, filename="qr")

    return qr
