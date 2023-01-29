import datetime as dt
import flask as fl
import logging as lg
from random import choices
from pymorphy2 import MorphAnalyzer

from data import db_session as d_s
from data.files import File

SYMBOLS = list('1234567890!@#$%^&*()~`-=_+ qwertyuiop[]asdfghjkl;zxcvbnm,./\
QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?')
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
BAD_CHARS = {' ', '/', '\\', '&', '?', '@', '"', "'", '(', ')'}
_DEFAULT = int('abcdef', 36)
_MAX = int('zzzzzz', 36)

_word_analyzer = MorphAnalyzer()
WORD_HOUR = _word_analyzer.parse('час')[0]
WORD_MINUTE = _word_analyzer.parse('минута')[0]

lg.basicConfig(level='INFO',
               format='%(asctime)s %(levelname)s %(filename)s %(message)s')


class Session:
    _ADDED_FILE_INFO = 'added_file_info'
    _FOUND_FILE_INFO = 'found_file_info'

    class Saver:
        def __init__(self, **attrs):
            for key, val in attrs.items():
                setattr(self, key, val)

    def get_added_file_info(self):
        if Session._ADDED_FILE_INFO not in fl.session:
            return None
        return Session.Saver(**fl.session[Session._ADDED_FILE_INFO])

    def set_added_file_info(self, name, key, link, hours: int):
        fl.session[Session._ADDED_FILE_INFO] = {
            'name': name,
            'key': key,
            'link': link,
            'hours': hours,
        }

    def get_found_file_info(self):
        if Session._FOUND_FILE_INFO not in fl.session:
            return None
        return Session.Saver(**fl.session[Session._FOUND_FILE_INFO])

    def set_found_file_info(self, name, key, link, life_time):
        fl.session[Session._FOUND_FILE_INFO] = {
            'name': name,
            'key': key,
            'link': link,
            'life_time': life_time,
        }


class Errors:
    NO_FILE = 'Вы не выбрали файл.'
    SAVE_ERROR = 'Не удалось сохранить файл. \
Попробуйте другой файл или повторите попытку позже.'
    FILE_NOT_FOUND = 'Файл под таким ключом не найден. \
Вы уверены, что он верный?'


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


def get_life_time(date):
    delta = date - dt.datetime.today()
    secs = delta.total_seconds()
    if secs < 0:
        return
    hours = int(secs // 3600)
    minutes = int(secs % 3600 // 60)
    return f'\
{hours} {WORD_HOUR.inflect({"accs"}).make_agree_with_number(hours).word} \
{minutes} {WORD_MINUTE.inflect({"accs"}).make_agree_with_number(minutes).word}'


def format_file_name(name):
    for char in BAD_CHARS:
        name = name.replace(char, '_')
    return name
