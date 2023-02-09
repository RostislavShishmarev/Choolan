import os

import flask as fl
import datetime as dt
import logging as lg
from random import choices
from pymorphy2 import MorphAnalyzer
from json import load as load_json_file

from data import db_session as d_s
from data.files import File


class Attributor:
    """Класс, сохраняющий вложенные словари в виде вложенных объектов
    (ключи словаря = атрибуты объекта). Чтобы словарь не становился объектом,
    в него нужно добавить значение True под ключом '.no_deserialize'
    (в итоговом объекте не сохраняются). Внутри него все словари будут таким
    же образом преобразованы в объекты."""
    @staticmethod
    def init(dict_):
        """Метод инициализации (вместо __init__)"""
        at = Attributor()
        for key, val in dict_.items():
            if isinstance(val, dict):
                if val.get(".no_deserialize", False):
                    setattr(at, key, Attributor._make_dict(val))
                else:
                    setattr(at, key, Attributor.init(val))
            elif not key.startswith('.'):
                setattr(at, key, val)
        return at

    @staticmethod
    def _make_dict(dict_):
        at = {}
        for key, val in dict_.items():
            if isinstance(val, dict):
                if val.get(".no_deserialize", False):
                    at[key] = Attributor._make_dict(val)
                else:
                    at[key] = Attributor.init(val)
            elif not key.startswith('.'):
                at[key] = val
        return at


with open('config.json', encoding='utf-8') as file:
    _dict_config = load_json_file(file)
CONFIG = Attributor.init(_dict_config)

_DEFAULT = int(CONFIG.consts.default_file_key, 36)
_MAX = int(CONFIG.consts.max_file_key, 36)

_word_analyzer = MorphAnalyzer()
WORD_HOUR = _word_analyzer.parse('час')[0]
WORD_MINUTE = _word_analyzer.parse('минута')[0]

lg.basicConfig(level=CONFIG.base.logging_level,
               format=CONFIG.base.logging_format)


class Session:
    _ADDED_FILE_INFO = 'added_file_info'
    _FOUND_FILE_INFO = 'found_file_info'

    def get_added_file_info(self):
        if Session._ADDED_FILE_INFO not in fl.session:
            return None
        return Attributor.init(fl.session[Session._ADDED_FILE_INFO])

    def set_added_file_info(self, **info_items):
        fl.session[Session._ADDED_FILE_INFO] = {}
        self._set_added_file_info_items(info_items)

    def update_added_file_info(self, **info_items):
        fl.session[Session._ADDED_FILE_INFO] = fl.session[
            Session._ADDED_FILE_INFO].copy()
        self._set_added_file_info_items(info_items)

    def _set_added_file_info_items(self, info_items):
        for key, val in info_items.items():
            fl.session[Session._ADDED_FILE_INFO][key] = val

    def get_found_file_info(self):
        if Session._FOUND_FILE_INFO not in fl.session:
            return None
        return Attributor.init(fl.session[Session._FOUND_FILE_INFO])

    def set_found_file_info(self, **info_items):
        fl.session[Session._FOUND_FILE_INFO] = {}
        self._set_found_file_info_items(info_items)

    def update_found_file_info(self, **info_items):
        fl.session[Session._FOUND_FILE_INFO] = fl.session[
            Session._FOUND_FILE_INFO].copy()
        self._set_found_file_info_items(info_items)

    def _set_found_file_info_items(self, info_items):
        for key, val in info_items.items():
            fl.session[Session._FOUND_FILE_INFO][key] = val


class Settings:
    COOKIE_AGE = 60 * 60 * 24 * 365 * 20
    def __init__(self, request):
        for key, val in CONFIG.default_settings.items():
            setattr(self, key, request.cookies.get(key, val))
        self.set_data = CONFIG.settings
        self.main_css_path = CONFIG.base.main_css_path

    def set_value(self, key, value):
        setattr(self, key, value)

    def save(self, response):
        for key in CONFIG.default_settings.keys():
            response.set_cookie(key, getattr(self, key),
                                max_age=Settings.COOKIE_AGE)


class Errors:
    NO_FILE = 'Вы не выбрали файл.'
    SAVE_ERROR = 'Не удалось сохранить файл. \
Попробуйте другой файл или повторите попытку позже.'
    FILE_NOT_FOUND = 'Файл под таким ключом не найден. \
Вы уверены, что он верный?'


def generate_secret_key():
    return ''.join(choices(CONFIG.consts.secret_key_alpha, k=250))


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
        result = CONFIG.consts.file_key_alpha[index] + result
    return result


def get_life_time(death_date):
    delta = death_date - dt.datetime.today()
    secs = delta.total_seconds()
    if secs < 0:
        return
    hours = int(secs // 3600)
    minutes = int(secs % 3600 // 60)
    return f'\
{hours} {WORD_HOUR.inflect({"accs"}).make_agree_with_number(hours).word} \
{minutes} {WORD_MINUTE.inflect({"accs"}).make_agree_with_number(minutes).word}'


def format_file_name(name):
    for char in CONFIG.consts.bad_chars:
        name = name.replace(char, '_')
    return name


def format_file_key(key):
    return key.replace(' ', '').replace('-', '').lower()


def clay_css_files():
    if os.path.exists(CONFIG.base.main_css_path):
        os.remove(CONFIG.base.main_css_path)

    result_css_data = ''
    root_css_path = os.path.dirname(CONFIG.base.main_css_path)
    for name in CONFIG.style_files_names:
        css_file_path = os.path.join(root_css_path, name)
        if os.path.isdir(css_file_path):
            continue
        with open(css_file_path, encoding='utf-8') as f:
            result_css_data += f.read() + '\n'

    with open(CONFIG.base.main_css_path, mode='w', encoding='utf-8') as f:
        f.write(result_css_data)
