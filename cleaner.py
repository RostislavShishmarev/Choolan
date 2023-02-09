import os
import shutil
from helpers import lg, get_life_time, CONFIG

from data import db_session as d_s
from data.files import File


def clean_files():
    lg.info('Start cleaning files...')
    db_sess = d_s.create_session()
    files = db_sess.query(File).all()

    except_folders = []
    for file in files:
        time = get_life_time(file.death_date)
        if time is None:
            db_sess.delete(file)
            delete_real_file_if_possible(file)
        else:
            except_folders.append(file.folder_path)
    db_sess.commit()

    _clean_files_directory_except(except_folders)
    lg.info('Files cleaned successfully!')


def _clean_files_directory_except(except_folders):
    for folder in os.listdir('files'):
        path = os.path.join('files', folder)
        if path not in except_folders:
            shutil.rmtree(path, ignore_errors=True)


def delete_real_file_if_possible(file):
    try:
        delete_real_file(file)
    except Exception as ex:
        lg.error(
            f'Can not delete file {file.folder_path}/{file.name}: ' +
            str(ex)
        )
        return False
    return True


def delete_real_file(file):
    shutil.rmtree(file.folder_path)
    lg.info(f'Successfully deleted file {file.folder_path}/{file.name}')


if __name__ == '__main__':
    d_s.global_init(CONFIG.base.db_path)
    clean_files()
