from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from urllib import parse
import re

from ping import ping
from secrets import ROUTER_USERNAME, ROUTER_PASSWORD

MAC_LOOKUPS = {
    'F8:F0:05:A6:C1:30': 'arduino'
}

class Router(object):
    
    ADDRESS = '192.168.0.1'

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.auth = HTTPBasicAuth(kwargs['username'], kwargs['password'])

        self.test_connection(tries=3)

        self._get_devices()

    def test_connection(self, timeout=1, tries=3):
        for i in range(tries):  
            retval = ping(self.ADDRESS, timeout=timeout).returncode
            if retval == 0:
                print('Established connection to router at {}.'.format(self.ADDRESS))
                return

        raise ConnectionError('Unable to reach router at {}.'.format(self.ADDRESS))                

    def _get_html(self, **kwargs):
        url = parse.urlunsplit(('http', self.ADDRESS, 'RgAttachedDevices.asp', '', ''))
        s = kwargs.get('session', requests.session())
        s.auth = self.auth
        r = s.get(url)
        while not r.ok:
            print('Router requests failed with status code {0}, message {1}.\nRetrying...'.format(r.status_code, r.text))
            r = s.get(url)

        if parse.urlsplit(r.url).path.strip('/') == 'MultiLogin.asp':
            # print('Encountered ''new device'' page.')
            form = BeautifulSoup(r.text, 'html.parser').find(id='target')
            data = {i.attrs.get('name', ''):i.attrs.get('value', '') for i in form.find_all('input')}
            data['Act'] = 'yes'
            data.pop('')
            data['yes'] = 'yes'
            dest = parse.urljoin(r.url, form.attrs['action'])

            s.post(dest, data=data)
            
            return self._get_html(session=s)

        return r.text

    def _cleanup(self, string):
        s = string.replace('&nbsp;', ' ')
        return s.strip()

    def _parse_html(self, page):
        soup = BeautifulSoup(page, 'html.parser')

        self.title = soup.find('title').string

        js = [s for s in soup.find_all('script') if s.string is not None][0].string

        devices = []
        wired = re.findall(r'new CPE_Info\((.+)\)', js)
        for w in wired:
            fields = re.findall(r'"([^"]+)"', w)
            d = {
                'wireless': False,
                'hostname': self._cleanup(fields[0]),
                'status': self._cleanup(fields[1]),
                'ip_address': self._cleanup(fields[2]),
                'mac_address': self._cleanup(fields[3])
            }
            if len(d['hostname']) == 0:
                d['hostname'] = MAC_LOOKUPS.get(d['mac_address'], '')

            devices.append(d)

        wireless = re.findall(r'new WLCPE_Info\((.+)\)', js)
        for w in wireless:
            fields = re.findall(r'"([^"]+)"', w)
            d = {
                'wireless': True,
                'hostname': self._cleanup(fields[0]),
                'status': self._cleanup(fields[1]),
                'ip_address': self._cleanup(fields[2]),
                'rssi': float(self._cleanup(fields[3])),
                'mac_address': self._cleanup(fields[4]),
                'is_guest': bool(int(self._cleanup(fields[5])))
            }
            if len(d['hostname']) == 0:
                d['hostname'] = MAC_LOOKUPS.get(d['mac_address'], '')

            devices.append(d)

        self.devices = devices

        self.retrieved = True
        

    def _get_devices(self):
        page = self._get_html()
        self._parse_html(page)

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

if __name__ == '__main__':
    rtr = Router(username=ROUTER_USERNAME, password=ROUTER_PASSWORD)
    print(rtr.devices)

        
