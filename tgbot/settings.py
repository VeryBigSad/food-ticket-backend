import os
import datetime


EXPIRATION_TIME = datetime.timedelta(minutes=15)
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
