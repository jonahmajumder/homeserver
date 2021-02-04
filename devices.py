import random
from phue import Bridge, Light
from wemo import Wemo
from router import Router
from secrets import ROUTER_USERNAME, ROUTER_PASSWORD
import requests
import json

class ArduinoRelay:
    def __init__(self, *args):
        self.ip = args[0]

        if len(args) > 1:
            self.name = args[1]
        else:
            self.name = 'Arduino Relay'

    def _get_data(self):
        return requests.get('http://{}'.format(self.ip)).json()

    def _set_data(self, data):
        return requests.post('http://{}'.format(self.ip), data=json.dumps(data)).json()

    def status(self):
        return self._get_data()['state']

    def on(self):
        self._set_data({'state': False})

    def off(self):
        self._set_data({'state': True})

    def identify(self):
        return self.name


class Device:
    def __init__(self, obj):
        self.obj = obj
        if isinstance(obj, Light):
            def turn_on(): obj.on = True
            self.turn_on = turn_on
            def turn_off(): obj.on = False
            self.turn_off = turn_off
            def status(): return obj.on
            self.status = status
            def identify(): return obj.name
            self.identify = identify
            self.type = 'Hue'
        elif isinstance(obj, Wemo):
            self.turn_on = obj.on
            self.turn_off = obj.off
            self.status = obj.status
            self.identify = obj.identify
            self.type = 'Wemo'
        elif isinstance(obj, ArduinoRelay):
            self.turn_on = obj.on
            self.turn_off = obj.off
            self.status = obj.status
            self.identify = obj.identify
            self.type = 'Arduino Relay'
        else:
            self.on = bool(random.randint(0,1))
            def turn_on(): self.on = True
            self.turn_on = turn_on
            def turn_off(): self.on = False
            self.turn_off = turn_off
            def status(): return self.on
            self.status = status
            def identify(): return 'Dummy Object'
            self.identify = identify
            self.type = 'Dummy'

def retrieve_devices():
    rtr = Router(username=ROUTER_USERNAME, password=ROUTER_PASSWORD)

    bridge_ip = rtr.hostname_to_ip('Philips-hue')
    b = Bridge(bridge_ip)
    lights = [l for l in b.lights if l.reachable]

    wemo_ips = [d['ip_address'] for d in rtr.devices if 'wemo' in d['hostname']]
    wemos = [Wemo(ip) for ip in wemo_ips]

    arduino_ips = [d['ip_address'] for d in rtr.devices if 'arduino' in d['hostname']]
    arduinos = [ArduinoRelay(ip) for ip in arduino_ips]

    return [Device(d) for d in lights + wemos + arduinos]

def dummy_list(n=5):
    return [Device(None) for i in range(n)]

