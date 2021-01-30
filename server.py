from http import HTTPStatus
from functools import wraps
from pathlib import Path

from flask import (Flask, 
    request, make_response,
    render_template
)

from devices import device_list

from secrets import USERNAME, PASSWORD

app = Flask(__name__)

def protected(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth is not None:
            if auth.username == USERNAME and auth.password == PASSWORD:
                return func(*args, **kwargs)

        return make_response(
            '<h2>Incorrect authorization.</h2>',
            HTTPStatus.UNAUTHORIZED.value,
            {'WWW-Authenticate': 'Basic realm="Login required"'}
        )

    return decorated


@app.route('/')
@app.route('/index')
@protected
def index():
    username = request.authorization.username
    names = [d.identify() for d in device_list]
    links = ['/device{}'.format(i) for i in range(len(device_list))]
    return render_template('index.html', title='Index', username=username, names=names, links=links)


def valid_device_num(strnum):
    try:
        device_list[int(strnum)]
        return True
    except:
        return False

@app.route('/device<num>', methods=['GET', 'POST'])
@protected
def device(num):
    if valid_device_num(num):
        dev = device_list[int(num)]

        if request.method == 'POST':
            newstate = bool(int(request.form['state']))
            dev.turn_on() if newstate else dev.turn_off()

        return render_template('binarydevice.html', name=dev.identify(), link='index', state=dev.status())
    else:
        return make_response(
            '<h2>Device not found!</h2>',
            HTTPStatus.NOT_FOUND.value
        )

