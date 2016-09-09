#!/usr/bin/env python

import os.path
import threading
from plover.machine.registry import machine_registry, NoSuchMachineException
from plover.virtualstenomachine.machine.machinenetwork import StenoMachineServer

class MachineInputBase(object):
	"""The base class for stenotype machine input"""

	def __init__(self):
		self.subscribers = []
		
	def add_callback(self, callback):
		"""Subscribe to input."""
		
		self.subscribers.append(callback)

	def remove_callback(self, callback):
		"""Unsubscribe from input"""
		
		self.subscribers.remove(callback)

	def start_input(self):
		"""Begin listening for input."""
		pass

	def stop_input(self):
		"""End listening for input."""
		pass
	
	def _notify(self, input):
		"""Invoke the callback of each subscriber with the given argument."""
		print "notify"
		for callback in self.subscribers:
			callback(input)
			
	def get_info(self):
		return "Input:"
	
	def _error(self, msg):
		raise InputError(msg)

class MachineInputFile(MachineInputBase):
	"""The file input class for stenotype machine input"""

	def __init__(self, filename):
		if not os.path.isfile(filename):
			self._error("File not found")
		self.filename = filename
		try:
			MachineInputBase.__init__(self)
			self.file = open(filename, 'r')
		except IOError as e:
			self._error("File could not be opened")			
		
	def start_input(self):
		for line in self.file:
			for input in line.split():
				if input:
					self._notify(input)
					
	def stop_input(self):
		self.file.close()
	
	def get_info(self):
		return "Input: File input \nfile: {}".format(self.filename)
					
class MachineInputNetwork(MachineInputBase):
	"""The network input from another virtual steno machine class for stenotype machine input"""

	def __init__(self, HOST, PORT):
		try:
			MachineInputBase.__init__(self)
			self.server = StenoMachineServer(HOST, PORT, self._notify)
			self.HOST = HOST
			self.PORT = PORT
		except:
			self._error("Could not start network")			
		
	def start_input(self):
		self.server.start()
		
	def stop_input(self):
		self.server.stop()
		
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT
	
	def get_info(self):
		return "Input: Network input \nHOST: {} \tPORT: {}".format(self.HOST, str(self.PORT))

class MachineInputPhysical(MachineInputBase):
	"""The input class for stenotype machine from physical machines"""

	def __init__(self, machine_type, machine_options):
		MachineInputBase.__init__(self)
		try:
			self.machine = machine_registry.get(machine_type)(machine_options)
			self.machine_type = machine_type
		except NoSuchMachineException as e:
			raise InvalidConfigurationError(unicode(e))	
		
	def start_input(self):
		print "start_input"
		self.machine.add_stroke_callback(self._notify)
		self.machine.start_capture()
					
	def stop_input(self):
		self.machine.stop_capture()
	
	def get_info(self):
		return "Input: Machine input \nMachine type: {}".format(self.machine_type)
		

class InputError(Exception):
	"""Exception raised for errors in the input."""

	def __init__(self, msg):
		self.value = msg