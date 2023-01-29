import os
import shutil
import datetime as dt
import requests as rq
import flask as fl
from flask import render_template, request, redirect, send_from_directory

from data import db_session as d_s
from data.files import File

from helpers import lg, generate_secret_key, generate_file_key, Errors,\
    Session, WORD_HOUR

SITE_DOMAIN = '127.0.0.1:8080'
app = fl.Flask(__name__)
key = generate_secret_key()
app.config['SECRET_KEY'] = key
app.config['JSON_AS_ASCII'] = False
app.debug = True

user_session = Session()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET'])
@app.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        pass
    return render_template('Get.html')


@app.route('/put', methods=['GET', 'POST'])
def put():
    if request.method == 'POST':
        file = request.files['loaded_file']
        hours = int(request.form['life_hours'])

        if not file:
            return render_template('Put.html', error_text=Errors.NO_FILE,
                                   hour_value=hours)

        key = generate_file_key()
        path = f'files/{key}'
        name = file.filename
        link = f'https://{SITE_DOMAIN}/' + path + '/' + name
        death_date = dt.datetime.today() + dt.timedelta(hours=hours)

        try:
            os.mkdir(path)
            file.save(path + '/' + name)
        except Exception as ex:
            lg.error("Could not save file: " + str(ex))
            shutil.rmtree(path, ignore_errors=True)
            return render_template('Put.html', error_text=Errors.SAVE_ERROR,
                                   hour_value=hours)

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
    return render_template('Found.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('About.html')


if __name__ == '__main__':
    d_s.global_init('db/ch_files.sqlite')
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)
