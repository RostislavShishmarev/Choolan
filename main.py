import os
import shutil
import requests as rq
import flask as fl
from flask import render_template, request, redirect, send_from_directory

from helpers import lg, generate_secret_key

app = fl.Flask(__name__)
key = generate_secret_key()
app.config['SECRET_KEY'] = key
app.config['JSON_AS_ASCII'] = False


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
    return render_template('Put.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('About.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='127.0.0.1', port=port)
