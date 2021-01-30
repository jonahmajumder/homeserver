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
        elif isinstance(obj, Wemo):
            self.turn_on = obj.on
            self.turn_off = obj.off
            self.status = obj.status
            self.identify = obj.identify
        else:
            raise Exception('Unrecognized device!')

rtr = Router(username=ROUTER_USERNAME, password=ROUTER_PASSWORD)

bridge_ip = rtr.hostname_to_ip('Philips-hue')
b = Bridge(bridge_ip)
lights = [l for l in b.lights if l.reachable]

wemo_ips = [d['ip_address'] for d in rtr.devices if 'wemo' in d['hostname']]
wemos = [Wemo(ip) for ip in wemo_ips]

device_list = [Device(d) for d in lights + wemos]
