import SocketServer
import socket
import threading

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 12345

class StenoMachineServer(object):

	def __init__(self, HOST, PORT, callback):
		self.HOST = HOST
		self.PORT = PORT
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.HOST, self.PORT))
		self.callback = callback
		
	def start(self):
		self.server_thread = threading.Thread(target=self.handle)
		self.server_thread.daemon = True
		self.server_thread.start()
	
	def handle(self):
		self.socket.listen(1)

		while True:
			self.connection, self.client_address = self.socket.accept()

			while True:
				data = self.connection.recv(1024).strip()

				if data:
					self.callback(data)


	def stop(self):
		self.socket.close()
		
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT

class StenoMachineClient(object):
	
	def __init__(self, HOST, PORT):
		self.HOST = HOST
		self.PORT = PORT
		
	def start(self):
		self.socket = socket.create_connection((self.HOST, int(self.PORT)), 1000)
		
	def read(self):
		received = self.socket.recv(1024)
		return received
		
	def send(self, msg):
		self.socket.sendall(msg)
		
	def stop(self):
		try:
			self.socket.close()
		except Exception,e:
			# Thrown when no socket was created due to a connection error
			pass
