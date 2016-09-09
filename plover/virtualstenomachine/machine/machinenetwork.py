import SocketServer
import socket
import threading

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 12345
	
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

class RequestHandler(SocketServer.BaseRequestHandler):

	def __init__(self, callback, *args, **keys):
		self.callback = callback
		SocketServer.BaseRequestHandler.__init__(self, *args, **keys)

	def handle(self):
		data = self.request.recv(1024).strip()
		self.callback(data)

class StenoMachineServer():

	def __init__(self, HOST, PORT, callback):
		self.HOST = HOST
		self.PORT = PORT
		self.server = ThreadedTCPServer((HOST, PORT), lambda *args, **keys: RequestHandler(callback, *args, **keys))
		
	def start(self):
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = True
		self.server_thread.start()
	
	def stop(self):
		self.server.shutdown()
		
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT

class StenoMachineClient():
	
	def __init__(self, HOST, PORT):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def start(self):
		self.socket.connect((HOST, PORT))
		
	def read(self):
		received = sock.recv(1024)
		return received
		
	def send(self, msg):
		self.socket.sendall(msg)
		
	def stop(self):
		self.socket.close()
