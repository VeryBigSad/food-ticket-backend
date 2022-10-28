import random
import string


def random_secret_code():
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for i in range(6)]
    )
