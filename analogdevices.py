import random
from phue import Bridge, Light
from router import Router
from secrets import ROUTER_USERNAME, ROUTER_PASSWORD
import requests
import json

class AnalogDevice:
    def __init__(self, obj):
        self.obj = obj
        if isinstance(obj, Light):
            def turn_on(): obj.on = True
            self.turn_on = turn_on
            def turn_off(): obj.on = False
            self.turn_off = turn_off
            def onoff_status(): return obj.on
            self.onoff_status = onoff_status
            def set_level(l): obj.brightness = max(0, min(int(l/100*255), 255)) # level is 0 to 100
            self.set_level = set_level
            def get_level(): return obj.brightness/255*100
            self.get_level = get_level
            def identify(): return obj.name
            self.identify = identify
            self.type = 'Hue'
        else:
            self.on = bool(random.randint(0,1))
            self.level = random.randint(0,100)
            def turn_on(): self.on = True
            self.turn_on = turn_on
            def turn_off(): self.on = False
            self.turn_off = turn_off
            def onoff_status(): return self.on
            self.onoff_status = onoff_status
            def set_level(l): self.level = max(0, min(l, 100))
            self.set_level = set_level
            def get_level(): return self.level
            self.get_level = get_level
            def identify(): return 'Dummy Object'
            self.identify = identify
            self.type = 'Dummy'

def retrieve_analogdevices():
    rtr = Router(username=ROUTER_USERNAME, password=ROUTER_PASSWORD)

    bridge_ip = rtr.hostname_to_ip('Philips-hue')
    b = Bridge(bridge_ip)
    lights = [l for l in b.lights if l.reachable]

    return [AnalogDevice(d) for d in lights]

def dummy_list(n=5):
    return [AnalogDevice(None) for i in range(n)]

