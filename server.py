from http import HTTPStatus
from functools import wraps
from pathlib import Path
import json
from datetime import datetime

start = datetime.now()

from flask import (Flask, 
    request, make_response,
    render_template
)

from devices import retrieve_devices, dummy_list
from sensors import retrieve_sensors

device_list = retrieve_devices()
sensor_list = retrieve_sensors()
# device_list = dummy_list()

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

@app.route('/status')
def status():
    current = datetime.now()
    d = {
        'status': 'ok',
        'age': int((current - start).total_seconds())
    }
    return json.dumps(d)

@app.route('/')
@app.route('/index')
@protected
def index():
    username = request.authorization.username

    if request.args.get('format', 'html') == 'json':
        device_dicts = [dict(
            link='/device{}'.format(i),
            name=d.identify(),
            type=d.type,
            state=d.status()
            ) for (i,d) in enumerate(device_list)] # wifi binary devices
        sensor_dicts = [dict(
            link='/sensor{}'.format(i),
            name=s.identify(),
            type=s.type,
            value=s.value()
            ) for (i,s) in enumerate(sensor_list)] # sensors
        dicts = device_dicts + sensor_dicts
        return json.dumps(dicts)
    else:
        device_previews = [render_template(
            'device_preview.html',
            link='/device{}'.format(i),
            name=d.identify(),
            type=d.type,
            ind_color='lawngreen' if d.status() else 'darkgreen'
            ) for (i,d) in enumerate(device_list)] # wifi binary devices
        sensor_previews = [render_template(
            'sensor_preview.html',
            link='/sensor{}'.format(i),
            name=s.identify(),
            type=s.type,
            value=s.valuestr()
            ) for (i,s) in enumerate(sensor_list)] # sensors
        previews = device_previews + sensor_previews
        return render_template('index.html', title='home', username=username, previews=previews)

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
            newstate = request.json['state']
            dev.turn_on() if newstate else dev.turn_off()

        if request.args.get('format', 'html') == 'json':
            return json.dumps(dict(name=dev.identify(), state=dev.status()))
        else:
            return render_template('binarydevice.html', name=dev.identify(), state=dev.status())
    else:
        if request.args.get('format', 'html') == 'json':
            msg = json.dumps(dict(error='Device not found!'))
        else:
            msg = '<h2>Device not found!</h2>'
        
        return make_response(msg, HTTPStatus.NOT_FOUND.value)
        
def valid_sensor_num(strnum):
    try:
        sensor_list[int(strnum)]
        return True
    except:
        return False


@app.route('/sensor<num>', methods=['GET'])
@protected
def sensor(num):
    if valid_sensor_num(num):
        s = sensor_list[int(num)]

        if request.args.get('format', 'html') == 'json':
            return json.dumps(dict(name=s.identify(), value=s.value()))
        else:
            return render_template('sensor.html', name=s.identify(), quantity=s.quantity, value=s.valuestr())
    else:
        if request.args.get('format', 'html') == 'json':
            msg = json.dumps(dict(error='Sensor not found!'))
        else:
            msg = '<h2>Sensor not found!</h2>'
        
        return make_response(msg, HTTPStatus.NOT_FOUND.value)
