from phue import Bridge

b = Bridge('192.168.0.5')
b.connect()
lights = b.lights