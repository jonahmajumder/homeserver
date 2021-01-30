from phue import Bridge
from wemo import Wemo
from router import Router

from secrets import ROUTER_USERNAME, ROUTER_PASSWORD

rtr = Router(username=ROUTER_USERNAME, password=ROUTER_PASSWORD)

bridge_ip = rtr.hostname_to_ip('Philips-hue')
print(bridge_ip)

wemo_ips = [d['ip_address'] for d in rtr.devices if 'wemo' in d['hostname']]
print(wemo_ips)