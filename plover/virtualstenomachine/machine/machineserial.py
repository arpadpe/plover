#!/usr/bin/env python

import sys
import os
import subprocess
import threading
import time

def create_serial_port(port1, port2):
	if os.path.isfile(port1):
		raise SerialError("{} port already used".format(port1))
		
	if os.path.isfile(port2):
		raise SerialError("{} port already used".format(port2))

	if sys.platform.startswith('win32'):
		return
	elif sys.platform.startswith('linux'):
		t = threading.Thread(target=_start_socat, args=(port1, port2))
        t.daemon = True
        t.start()

        time.sleep(1)

        if not t.isAlive():
        	raise SerialError("Error creating ports.")

	elif sys.platform.startswith('darwin'):
		# TODO
		pass
		
def _start_socat(port1, port2):
	args = ['socat', 'pty,raw,echo=0,link='+str(port1), 'pty,raw,echo=0,link='+str(port2)]
	child = subprocess.Popen(args, stdout=subprocess.PIPE)
	out,err = child.communicate()

def virtual_serial_ports_available():
	if sys.platform.startswith('win32'):
		return False
	elif sys.platform.startswith('linux'):
		return True
	elif sys.platform.startswith('darwin'):
		return False

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
		return ['/tmp/ttyV1','/tmp/ttyV2']
	elif sys.platform.startswith('darwin'):
		# TODO
		pass
		
class SerialError(Exception):
	"""Serial exception raised due to an error creating a serial socket."""

	def __init__(self, msg):
		self.value = msg