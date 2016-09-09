#!/usr/bin/env python

import sys
import os
import subprocess

socat_port = None

def create_serial_port(port1, port2):
	if os.path.isfile(port1):
		raise SerialError("{} port already used".format(port1))
		
	if os.path.isfile(port2):
		raise SerialError("{} port already used".format(port2))
		
	if sys.platform.startswith('linux'):
		try:
			args = ['socat', '-d', '-d', 'pty,raw,echo=0,link='+str(port1), 'pty,raw,echo=0,link='+str(port2)]
			socat_port = subprocess.Popen(args)		
		except:
			raise SerialError("Error creating ports.")
	elif sys.platform.startswith('darwin'):
		# TODO
		pass
		
def close_serial_port():		
	if sys.platform.startswith('linux'):	
		if socat_port:
			socat_port.terminate()
	elif sys.platform.startswith('darwin'):
		# TODO
		pass

def get_default_ports():
	if sys.platform.startswith('win32'):
		return ['COM1','COM2']
	elif sys.platform.startswith('linux'):
		return ['/tmp/port1','/tmp/port2']
	elif sys.platform.startswith('darwin'):
		# TODO
		pass
		
class SerialError(Exception):
	"""Serial exception raised due to an error creating a serial socket."""

	def __init__(self, msg):
		self.value = msg