#!/usr/bin/env python

import serial
import plover.virtualstenomachine.machine.machineserial as machineserial
from plover.virtualstenomachine.machine.machinenetwork import StenoMachineClient

class MachineOutputBase:
		
	def start(self):
		pass
		
	def stop(self):
		pass
		
	def send(self, msg):
		pass
		
	def get_info(self):
		return "Output:"
		
	def _error(self, msg):
		raise OutputError(msg)

class MachineOutputSerial:

	def __init__(self, params):
		"""Monitor the stenotype over a serial port.

		Keyword arguments are the same as the keyword arguments for a
		serial.Serial object.

		"""
		self.serial_port = None
		self.serial_params = params['serial_params']
		self.port_in = params['port1']
		self.port_out = params['port2']
		self.machine_type = params['machine_type']
		
		try:
			machineserial.create_serial_port(self.port_in, self.port_out)
		except machineneserial.SerialError as e:
			self._error(e.value)
		
	def start(self):
		pass

	def stop(self):
		if self.serial_port:
			self.serial_port.close()
		
	def send(self, msg):
		pass

	@staticmethod
	def get_machine_info():
		"""Get the default options for this machine."""
		bool_converter = lambda s: s == 'True'
		sb = lambda s: int(float(s)) if float(s).is_integer() else float(s)
		return {
			'port': (None, str), # TODO: make first port default
			'baudrate': (9600, int),
			'bytesize': (8, int),
			'parity': ('N', str),
			'stopbits': (1, sb),
			'timeout': (2.0, float),
			'xonxoff': (False, bool_converter),
			'rtscts': (False, bool_converter)
		}
	
	def get_info(self):
		return "Output: Serial output\n "

class MachineOutputNetwork:

	def __init__(self, HOST, PORT):
		self.HOST = HOST
		self.PORT = PORT
		self.client = StenoMachineClient(HOST, PORT)
		
	def start(self):
		try:
			self.client.start()
		except:
			self._error("Could connect to {}:{}".format(self.HOST, self.PORT))
		
	def stop(self):
		self.client.stop()
		
	def send(self, msg):
		self.client.send(msg)
	
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT
		
	def get_info(self):
		return "Output: Network output \nHOST: {} \tPORT: {}".format(self.HOST, str(self.PORT))
		
class OutputError(Exception):
	"""Exception raised for errors in the output."""

	def __init__(self, msg):
		self.value = msg