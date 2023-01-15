import logging as lg
from random import choices

SYMBOLS = list('1234567890!@#$%^&*()~`-=_+ qwertyuiop[]asdfghjkl;zxcvbnm,./\
QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?')

# Генерация ключа для формы
def generate_secret_key():
    return ''.join(choices(SYMBOLS, k=250))
