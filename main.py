import os
import shutil
import datetime as dt
import requests as rq
import flask as fl
from flask import render_template, request, redirect, send_from_directory

from data import db_session as d_s
from data.files import File

from helpers import lg, generate_secret_key, generate_file_key

SITE_DOMAIN = '127.0.0.1:8080'
app = fl.Flask(__name__)
key = generate_secret_key()
app.config['SECRET_KEY'] = key
app.config['JSON_AS_ASCII'] = False
app.debug = True


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
@app.route('/get', methods=['GET', 'POST'])
def get():
    return render_template('Get.html')


@app.route('/put', methods=['GET', 'POST'])
def put():
    if request.method == 'POST':
        file = request.files['loaded_file']

        key = generate_file_key()
        path = f'files/{key}'
        name = file.filename
        link = f'https://{SITE_DOMAIN}/' + path + '/' + name

        os.mkdir(path)
        file.save(path + '/' + name)

        hours = int(request.form['life_hours'])
        death_date = dt.datetime.today() + dt.timedelta(hours=hours)

        db_session = d_s.create_session()
        file = File(key=key,
                    name=name,
                    folder_path=path,
                    link=link,
                    death_date=death_date)
        db_session.add(file)
        db_session.commit()

        fl.session['added_file_info'] = {
            'name': name,
            'key': key,
            'link': link,
            'hours': hours,
        }
        return redirect('/uploaded')
    return render_template('Put.html')


@app.route('/uploaded', methods=['GET'])
def uploaded():
    return render_template('Uploaded.html')


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
