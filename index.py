import serial
import json
import requests
import SimpleHTTPServer
import SocketServer
import subprocess
from urlparse import urlparse, parse_qs
from time import sleep

serialEnabled=False
serverUri="http://localhost:4010"
PORT=3030


def rgb(r, g, b):
	global ser

	print "R", r, "G", g, "B", b
	if serialEnabled:
		ser.write(bytes(r+","+g+","+b))

class HttpHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()

			self.wfile.write('ok')
			return
	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', serverUri)
		SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')
		self.end_headers()
		return

	def do_POST(self):
		print(self.path)

		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('ok')

		if self.path == '/rgb':
			content_len = int(self.headers.getheader('content-length', 0))
			post_body = self.rfile.read(content_len)
			params = parse_qs(post_body.decode('utf-8')) 
			rgb(params['r'][0], params['g'][0], params['b'][0])

			return

		elif self.path == '/volume':
			content_len = int(self.headers.getheader('content-length', 0))
			post_body = self.rfile.read(content_len)
			params = parse_qs(post_body.decode('utf-8')) 
			print("volume", params['volume'])

			subprocess.call(["amixer", "set", "Master", params['volume'][0].strip()])

			return
		elif self.path == '/shutdown':
			subprocess.call(["sudo", "shutdown", "-h", "now"])
			return

try:

	with open('config.json') as f:
		Config = json.load(f)
		PORT=int(Config['port'])
		serverUri=Config['server']
		serialEnabled=Config['serialEnabled']


		vol=subprocess.check_output(["./getVolume.sh"])
		result = requests.post(serverUri+'/kiosk-volume', data={'volume':vol.replace('%','')})

		if serialEnabled:
			ser = serial.Serial(Config['serialDevice'], int(Config['serialPort']), timeout=0.5)

		httpd = SocketServer.TCPServer(("", PORT), HttpHandler)

		print "http server running on", PORT
		httpd.serve_forever()
		

		while True:
			if serialEnabled:
				data = ser.read(3)
			
				if len(data) > 0:
					print 'Button:', data.strip()
					result = requests.post(url=serverUri+'/button/'+data.strip())
					
except:
	try:
		httpd.socket.close()
	except:
		print('httpd was not started')

