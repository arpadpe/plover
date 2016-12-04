#!/usr/bin/env python

import serial
import plover.virtualstenomachine.machine.machineserial as machineserial
from plover.virtualstenomachine.machine.machinenetwork import StenoMachineClient
from plover.virtualstenomachine.machine.geminipr import VirtualStenotypeGeminiPr as geminipr
from plover.virtualstenomachine.machine.passport import VirtualStenotypePassport as passport
from plover.virtualstenomachine.machine.stentura import VirtualStenotypeStentura as stentura
from plover.virtualstenomachine.machine.txbolt import VirtualStenotypeTxBolt as txbolt


machines = { "Gemini PR" : geminipr, "Passport" : passport, "Stentura" : stentura, "TX Bolt" : txbolt}

class MachineOutputBase(object):
		
	def start(self):
		pass
		
	def stop(self):
		pass
		
	def send(self, msg):
		pass
		
	def get_info(self):
		return "Output:"
		
	def _error(self, msg):
		raise Exception(msg)

	def __repr__(self):
		return "MachineOutputBase()"

class MachineOutputSerial(MachineOutputBase):

	def __init__(self, params):
		"""Monitor the stenotype over a serial port.

		Keyword arguments are the same as the keyword arguments for a
		serial.Serial object.

		"""
		
		try:
			self.params = params
			self.serial_port = None
			self.machine_type = params['machine_type']
			self.machine_params = params['machine_options']
			self.machine = machines[self.machine_type](self.machine_params)
		except Exception, e:
			print Exception, str(e)
		
	def start(self):
		self.machine.start()

	def stop(self):
		self.machine.stop()
		if self.serial_port:
			self.serial_port.close()
			machineneserial.close_serial_port()
		
	def send(self, msg):
		self.machine.send(msg)

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
		return "Output: Serial output \nMachine type: {}".format(self.machine_type)

	def __repr__(self):
		return "MachineOutputSerial(%s)" % (self.params)

class MachineOutputNetwork(MachineOutputBase):

	def __init__(self, HOST, PORT):
		self.HOST = HOST
		self.PORT = PORT
		self.client = StenoMachineClient(HOST, PORT)
		
	def start(self):
		try:
			self.client.start()
		except Exception, e:
			self._error("Could not connect to %s:%s\n%s" % (self.HOST, self.PORT, e))
		
	def stop(self):
		self.client.stop()
		
	def send(self, msg):
		self.client.send(msg + '\n')
	
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT
		
	def get_info(self):
		return "Output: Network output \nHOST: {} \tPORT: {}".format(self.HOST, str(self.PORT))

	def __repr__(self):
		return "MachineOutputNetwork(%s, %s)" % (self.HOST, self.PORT)
