import os


def is_admin(phone):
    return phone == os.getenv('CLIENT_PHONE')
