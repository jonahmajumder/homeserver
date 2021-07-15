import random
from therm import Thermometer
		
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

