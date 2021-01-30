from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from urllib import parse
import re

from secrets import ROUTER_USERNAME, ROUTER_PASSWORD

class Router(object):
    """docstring for Router"""
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.address = args[0]
        self.auth = HTTPBasicAuth(kwargs['username'], kwargs['password'])

        self._get_devices()

    def _parse_html(self, page):
        soup = BeautifulSoup(page, 'html.parser')

        self.title = soup.find('title').text

        js = [s for s in soup.find_all('script') if 'src' not in s.attrs][0].text

        devices = []
        wired = re.findall(r'new CPE_Info\((.+)\)', js)
        for w in wired:
            fields = re.findall(r'"([^"]+)"', w)
            devices.append(
                {
                    'wireless': False,
                    'hostname': fields[0],
                    'status': fields[1],
                    'ip_address': fields[2],
                    'mac_address': fields[3]
                }
            )

        wireless = re.findall(r'new WLCPE_Info\((.+)\)', js)
        for w in wireless:
            fields = re.findall(r'"([^"]+)"', w)
            devices.append(
                {
                    'wireless': True,
                    'hostname': fields[0],
                    'status': fields[1],
                    'ip_address': fields[2],
                    'rssi': float(fields[3]),
                    'mac_address': fields[4],
                    'is_guest': bool(int(fields[5]))
                }
            )

        self.devices = devices

        self.retrieved = True
        

    def _get_devices(self):
        url = parse.urlunsplit(('http', self.address, 'RgAttachedDevices.asp', '', ''))
        r = requests.get(url, auth=self.auth)
        assert r.ok

        self._parse_html(r.text)

    def hostnames(self, refresh=False):
        self._get_devices() if refresh or not self.retrieved else None

        return [d['hostname'] for d in self.devices]

    def ip_to_hostname(self, ip, refresh=False):
        self._get_devices() if refresh or not self.retrieved else None

        matches = [d for d in self.devices if d['ip_address'] == ip]

        if len(matches) > 0:
            return matches[0]['hostname']
        else:
            return None

    def hostname_to_ip(self, hostname, refresh=False):
        self._get_devices() if refresh or not self.retrieved else None

        matches = [d for d in self.devices if d['hostname'] == hostname]

        if len(matches) > 0:
            return matches[0]['ip_address']
        else:
            return None


rtr = Router('192.168.0.1', username=ROUTER_USERNAME, password=ROUTER_PASSWORD)

        