import logging as lg
from random import choices

from data import db_session as d_s
from data.files import File

SYMBOLS = list('1234567890!@#$%^&*()~`-=_+ qwertyuiop[]asdfghjkl;zxcvbnm,./\
QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?')
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
_DEFAULT = int('abcdef', 36)
_MAX = int('zzzzzz', 36)


# Генерация ключа для формы
def generate_secret_key():
    return ''.join(choices(SYMBOLS, k=250))


def generate_file_key():
    db_session = d_s.create_session()
    res = db_session.query(File).all()
    if res:
        max_key = max(res, key=lambda x: x.id).key
        num_key = int(max_key, 36)
    else:
        num_key = _DEFAULT

    num_key += 1
    num_key %= _MAX

    result = ''
    while num_key > 0:
        index = num_key % 36
        num_key //= 36
        result = ALPHABET[index] + result
    return result
