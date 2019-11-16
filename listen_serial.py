import serial
import json
import requests
from time import sleep

serialEnabled=False
serverUri="http://localhost:4010"
PORT=3030

with open('config.json') as f:
	Config = json.load(f)
	PORT=int(Config['port'])
	serverUri=Config['server']
	serialEnabled=Config['serialEnabled']

	if serialEnabled:
		ser = serial.Serial(Config['serialDevice'], int(Config['serialPort']), timeout=0.5)

	print "serial server running on", int(Config['serialPort'])

	while True:
		if serialEnabled:
			data = ser.read(3)
		
			if len(data) > 0:
				print 'Button:', data.strip()
				url=serverUri+'/button/'+data.strip() 
				result = requests.post(url=serverUri+'/button/'+data.strip())