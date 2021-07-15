import os
import glob
import re
import random
import threading

class ThermometerError(Exception):
	pass

class Thermometer:
	GLOBPATH = '/sys/bus/w1/devices/28*/w1_slave'
	
	def __init__(self, *args, **kwargs):
		self.path = self.get_path()

		self.active = False
		self._value = float('nan')
		
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
		crcMatch = re.search(r'crc=[a-z0-9]{2}\s([A-Z]+)', lines[0])
		tempMatch = re.search(r't=(\d+)', lines[1])
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

	def sample_and_repeat(self, interval):
		self._value = self.get_temp_F()
		if self.active:
			threading.Timer(interval, self.sample_and_repeat, args=[interval]).start()

	def start_sampling(self, interval=1.0):
		self.active = True
		self.sample_and_repeat(interval)

	def stop_sampling(self):
		self.active = False
		

