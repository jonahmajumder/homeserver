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

from binarydevices import retrieve_binarydevices, dummy_list
from analogdevices import retrieve_analogdevices, dummy_list
from sensors import retrieve_sensors

binarydevice_list = retrieve_binarydevices()
analogdevice_list = retrieve_analogdevices()
device_list = binarydevice_list + analogdevice_list
# sensor_list = retrieve_sensors()
sensor_list = []
# device_list = dummy_list()

print('Found {:d} binary devices, {:d} analog devices, {:d} sensors'.format(
    len(binarydevice_list),
    len(analogdevice_list),
    len(sensor_list)
    )
)

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
        binarydevice_dicts = [dict(
            link='/binarydevice{}'.format(i),
            name=d.identify(),
            type=d.type,
            state=d.status()
            ) for (i,d) in enumerate(binarydevice_list)] # wifi binary devices
        sensor_dicts = [dict(
            link='/sensor{}'.format(i),
            name=s.identify(),
            type=s.type,
            value=s.value()
            ) for (i,s) in enumerate(sensor_list)] # sensors
        dicts = binarydevice_dicts + sensor_dicts
        return json.dumps(dicts)
        analogdevice_dicts = [dict(
            link='/analogdevice{}'.format(i),
            name=d.identify(),
            type=d.type,
            state=d.status(),
            level='{:.1f}'.format(d.get_level())
            ) for (i,d) in enumerate(analogdevice_list)] # analog devices
        dicts = binarydevice_dicts + sensor_dicts + analogdevice_dicts
        return json.dumps(dicts)
    else:
        binarydevice_previews = [render_template(
            'binarydevice_preview.html',
            link='/binarydevice{}'.format(i),
            name=d.identify(),
            type=d.type,
            ind_color='lawngreen' if d.status() else 'darkgreen'
            ) for (i,d) in enumerate(binarydevice_list)] # wifi binary devices
        sensor_previews = [render_template(
            'sensor_preview.html',
            link='/sensor{}'.format(i),
            name=s.identify(),
            type=s.type,
            value=s.valuestr()
            ) for (i,s) in enumerate(sensor_list)] # sensors
        analogdevice_previews = [render_template(
            'analogdevice_preview.html',
            link='/analogdevice{}'.format(i),
            name=d.identify(),
            type=d.type,
            state=d.status(),
            level='{:.1f}'.format(d.get_level()),
            ind_color='lawngreen' if d.status() else 'darkgreen'
            ) for (i,d) in enumerate(analogdevice_list)] # analog devices
        previews = binarydevice_previews + sensor_previews + analogdevice_previews
        return render_template('index.html', title='home', username=username, previews=previews)


@app.route('/binarydevice<num>', methods=['GET', 'POST'])
@protected
def binarydevice(num):
    if num.isnumeric() and int(num) in range(len(binarydevice_list)):
        bindev = binarydevice_list[int(num)]

        if request.method == 'POST':
            newstate = request.json['state']
            bindev.turn_on() if newstate else bindev.turn_off()

        if request.args.get('format', 'html') == 'json':
            return json.dumps(dict(name=bindev.identify(), state=bindev.status()))
        else:
            return render_template('binarydevice.html', name=bindev.identify(), state=bindev.status())
    else:
        if request.args.get('format', 'html') == 'json':
            msg = json.dumps(dict(error='Binary device not found!'))
        else:
            msg = '<h2>Binary device not found!</h2>'
        
        return make_response(msg, HTTPStatus.NOT_FOUND.value)


@app.route('/sensor<num>', methods=['GET'])
@protected
def sensor(num):
    if num.isnumeric() and int(num) in range(len(sensor_list)):
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


@app.route('/analogdevice<num>', methods=['GET', 'POST'])
@protected
def analogdevice(num):
    if num.isnumeric() and int(num) in range(len(analogdevice_list)):
        adev = analogdevice_list[int(num)]

        if request.method == 'POST':
            if 'state' in request.json:
                newstate = request.json['state']
                adev.turn_on() if newstate else adev.turn_off()
            if 'level' in request.json:
                newlevel = request.json['level']
                adev.set_level(int(newlevel))

        if request.args.get('format', 'html') == 'json':
            return json.dumps(dict(name=adev.identify(), state=adev.status(), level=adev.get_level()))
        else:
            return render_template('analogdevice.html', name=adev.identify(), state=adev.status(), level=adev.get_level())
    else:
        if request.args.get('format', 'html') == 'json':
            msg = json.dumps(dict(error='Analog device not found!'))
        else:
            msg = '<h2>Analog device not found!</h2>'
        
        return make_response(msg, HTTPStatus.NOT_FOUND.value)


@app.route('/device<num>', methods=['GET', 'POST'])
@protected
def device(num):
    if num.isnumeric() and int(num) in range(len(device_list)):
        dev = device_list[int(num)]

        if request.method == 'POST':
            if 'state' in request.json:
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

