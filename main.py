import os
import shutil
import datetime as dt
import flask as fl
from flask import render_template, request, redirect, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler

from data import db_session as d_s
from data.files import File

from helpers import lg, generate_secret_key, generate_file_key, Errors,\
    Session, WORD_HOUR, get_life_time, format_file_name

PROTOCOL = 'http'
SITE_DOMAIN = '127.0.0.1:8080'
app = fl.Flask(__name__)
key = generate_secret_key()
app.config['SECRET_KEY'] = key
app.config['JSON_AS_ASCII'] = False

user_session = Session()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
@app.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        key = request.form['file_key']
        db_sess = d_s.create_session()
        file = db_sess.query(File).filter(File.key == key).first()
        if file is None:
            return render_template('Get.html',
                                   error_text=Errors.FILE_NOT_FOUND,
                                   form_data=request.form)
        life_time = get_life_time(file.death_date)
        if life_time is None:
            delete_file(file)
            return render_template('Get.html',
                                   error_text=Errors.FILE_NOT_FOUND,
                                   form_data=request.form)
        user_session.set_found_file_info(
            name=file.name,
            key=file.key,
            link=file.link,
            life_time=life_time
        )
        if request.form['method'] == 'check_it':
            return redirect('/found')
        elif request.form['method'] == 'download_it':
            return redirect('/found?download=true')
    return render_template('Get.html')


@app.route('/put', methods=['GET', 'POST'])
def put():
    if request.method == 'POST':
        file = request.files['loaded_file']
        hours = int(request.form['life_hours'])

        if not file:
            return render_template('Put.html', error_text=Errors.NO_FILE,
                                   form_data=request.form)

        key = generate_file_key()
        path = f'files/{key}'
        name = format_file_name(file.filename)
        link = f'{PROTOCOL}://{SITE_DOMAIN}/' + path + '/' + name
        death_date = dt.datetime.today() + dt.timedelta(hours=hours)

        try:
            os.mkdir(path)
            file.save(path + '/' + name)
        except Exception as ex:
            lg.error("Could not save file: " + str(ex))
            shutil.rmtree(path, ignore_errors=True)
            return render_template('Put.html', error_text=Errors.SAVE_ERROR,
                                   form_data=request.form)

        db_session = d_s.create_session()
        file = File(key=key,
                    name=name,
                    folder_path=path,
                    link=link,
                    death_date=death_date)
        db_session.add(file)
        db_session.commit()

        user_session.set_added_file_info(name, key, link, hours)
        return redirect('/uploaded')
    return render_template('Put.html')


@app.route('/uploaded', methods=['GET'])
def uploaded():
    file_info = user_session.get_added_file_info()
    if file_info is None:
        fl.abort(404)
    word_hour_form = WORD_HOUR.inflect(
        {'gent'}).make_agree_with_number(file_info.hours).word
    return render_template('Uploaded.html', file_info=file_info,
                           word_hour_form=word_hour_form)


@app.route('/found', methods=['GET'])
def found():
    download = 'download' in request.args.keys()
    file_info = user_session.get_found_file_info()
    return render_template('Found.html', download=download,
                           file_info=file_info)


@app.route('/files/<path:path>')
def get_file(path):
    return fl.send_from_directory('files', path)


@app.route('/about', methods=['GET'])
def about():
    return render_template('About.html')


def clean_files():
    lg.info('Start cleaning files...')
    db_sess = d_s.create_session()
    files = db_sess.query(File).all()
    for file in files:
        time = get_life_time(file.death_date)
        if time is None:
            try:
                delete_file(file)
            except Exception as ex:
                lg.error(
                    f'Can not delete file {file.folder_path}/{file.name}: ' +
                    str(ex)
                )
                continue
            db_sess.delete(file)
    db_sess.commit()
    lg.info('Files cleaned successfully!')


def delete_file(file):
    shutil.rmtree(file.folder_path)
    lg.debug(f'Successfully deleted file {file.folder_path}/{file.name}')


if __name__ == '__main__':
    d_s.global_init('db/ch_files.sqlite')

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(clean_files, 'interval', minutes=30)
    scheduler.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)
