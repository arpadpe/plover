#!/usr/bin/env python

'''
from machineinput import MachineInputFile as Input
import machineinput
from machinenetwork import StenoMachineClient
import machinenetwork

from machineoutput import MachineOutputSerial

'''
'''
self.params = params
self.serial_port = None
self.serial_params = params['serial_params']
self.port_in = params['port1']
self.port_out = params['port2']
self.machine_type = params['machine_type']
self.machine_params = parans['machine_params']
'''

#machine = MachineOutputSerial({"machine_type" : "Stentura", "port1" : "COM1", "port2" : "COM2", "serial_params", {},"machine_params" : {}})


'''
def printinput(string):
	print string

client = StenoMachineClient(machinenetwork.DEFAULT_HOST, machinenetwork.DEFAULT_PORT)

client.send("alma")

'''

'''
try:
	input = Input('input.txt')
except machineinput.InputError as e:
	print e.value

def printinput(string):
	print string
	
input.add_callback(printinput)

input.start_input()
'''
'''
import SocketServer
import socket

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        #self.wfile.write(self.data.upper())

class RequestHandler(SocketServer.BaseRequestHandler):

	def __init__(self, callback, *args, **keys):
		self.callback = callback
		SocketServer.BaseRequestHandler.__init__(self, callback, *args, **keys)

	def handle(self):
		data = self.request.recv(1024).strip()
		self.callback(data)
		print data

if __name__ == "__main__":
    HOST, PORT = "localhost", 12345

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), RequestHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
'''

def printinput(string):
	print string

HOST = "localhost"
PORT = 12345

from machinenetwork import StenoMachineServer


server = StenoMachineServer(HOST, PORT, printinput)

server.handle()


'''
from machinenetwork import ThreadedTCPServer
from machinenetwork import RequestHandler

server = ThreadedTCPServer((HOST, PORT), lambda *args, **keys: RequestHandler(printinput, *args, **keys))
server.serve_forever()'''