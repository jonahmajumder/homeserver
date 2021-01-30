from phue import Bridge, Light
from wemo import Wemo
from router import Router

from secrets import ROUTER_USERNAME, ROUTER_PASSWORD

class Device:
    def __init__(self, obj):
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
        else:
            def turn_on(): print('Dummy on!')
            self.turn_on = turn_on
            def turn_off(): print('Dummy off!')
            self.turn_off = turn_off
            def status(): return True
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

    return [Device(d) for d in lights + wemos]

def dummy_list(n=5):
    return [Device(None) for i in range(n)]