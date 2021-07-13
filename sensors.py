import os
import glob
import re
import random

class ThermometerError(Exception):
	pass

class Thermometer:
	GLOBPATH = '/sys/bus/w1/devices/28*/w1_slave'
	
	def __init__(self, *args, **kwargs):
		self.path = self.get_path()
		
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		
	def get_path(self):
		matches = glob.glob(self.GLOBPATH)
		if len(matches) != 1:
			raise ThermometerError('Single IO file not found!')
		else:
			return matches[0]
			
	def read_raw(self):
		f = open(self.path)
		lines = f.readlines()
		f.close()
		if len(lines) != 2:
			raise ThermometerError('Thermometer did not output 2 lines!')
		else:
			return [l.strip() for l in lines] # remove whitespace
		
	def parse_raw(self, lines):
		crcMatch = re.search('crc=[a-z0-9]{2}\s([A-Z]+)', lines[0])
		tempMatch = re.search('t=(\d+)', lines[1])
		if crcMatch is None or tempMatch is None:
			raise ThermometerError('Unexpected thermometer output format!')
		else:
			crcValid = crcMatch.group(1) == 'YES'
			tempC = float(tempMatch.group(1))/1000
			return tempC, crcValid
			
	def get_temp_C(self):
		crc = False
		while not crc:
			lines = self.read_raw()
			tC, crc = self.parse_raw(lines)
		return tC
	
	@staticmethod
	def C2F(tC):
		tF = tC * 9.0/5.0 + 32
		return tF
		
	def get_temp_F(self):
		tC = self.get_temp_C()
		tF = self.C2F(tC)
		return tF
		
		
class Sensor:
	def __init__(self, obj):
		self.obj = obj
		if isinstance(obj, Thermometer):
			self.value = obj.get_temp_F
			self.valuestr = lambda: '{:.1f} °F'.format(self.value())
			self.identify = lambda: 'One-Wire Thermometer'
			self.quantity = 'Temperature'
			self.type = 'Thermometer'
		else:
			self.value = random.random
			self.valuestr = lambda: '{:.2f}'.format(self.value())
			self.identify = lambda: 'RNG'
			self.quantity = 'Random Number'
			self.type = 'Dummy'
			
def retrieve_sensors():
	sensors = []
	
	try:
		t = Thermometer()
		t.get_temp_F()
		sensors.append(Sensor(t))
	except ThermometerError:
		pass
	
	return sensors

