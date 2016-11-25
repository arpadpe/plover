#!/usr/bin/env python

import os.path
import threading
from plover.machine.registry import machine_registry, NoSuchMachineException
from plover.virtualstenomachine.machine.machinenetwork import StenoMachineServer
from plover import system

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

	def start_input(self, done):
		"""Begin listening for input."""
		pass

	def stop_input(self):
		"""End listening for input."""
		pass
	
	def _notify(self, input):
		"""Invoke the callback of each subscriber with the given argument."""
		print "notify", input
		for callback in self.subscribers:
			callback(input)
			
	def get_info(self):
		return "Input:"
	
	def _error(self, msg):
		raise InputError(msg)

	def __repr__(self):
		return "MachineInputBase()"

class MachineInputFile(MachineInputBase):
	"""The file input class for stenotype machine input"""

	def __init__(self, filename, delimiter=None):
		if not os.path.isfile(filename):
			self._error("File not found")
		self.filename = filename
		self.delimiter = delimiter if delimiter is not None else '\n'
		try:
			MachineInputBase.__init__(self)
			self.file = open(filename, 'r')
		except IOError as e:
			self._error("File could not be opened")			
		
	def start_input(self, done):
		for line in self.file:
			for input in line.strip().split(self.delimiter):
				if input:
					self._notify(input)
		done()
					
	def stop_input(self):
		self.file.close()
	
	def get_info(self):
		return "Input: File input \nfile: {}".format(self.filename)

	def __repr__(self):
		return "MachineInputFile(%s)" % (self.filename)
					
class MachineInputNetwork(MachineInputBase):
	"""The network input from another virtual steno machine class for stenotype machine input"""

	def __init__(self, HOST, PORT):
		try:
			MachineInputBase.__init__(self)
			self.server = StenoMachineServer(HOST, PORT, self._notify)
			self.HOST = HOST
			self.PORT = PORT
		except Exception, e:
			self._error("Could not start network\n%s" % e)
		
	def start_input(self, done):
		self.server.start()
		
	def stop_input(self):
		self.server.stop()
		
	def get_host(self):
		return self.HOST
		
	def get_port(self):
		return self.PORT
	
	def get_info(self):
		return "Input: Network input \nHOST: {} \tPORT: {}".format(self.HOST, str(self.PORT))

	def __repr__(self):
		return "MachineInputNetwork(%s, %s)" % (self.HOST, self.PORT)

class MachineInputPhysical(MachineInputBase):
	"""The input class for stenotype machine from physical machines"""

	def __init__(self, machine_type, machine_options):
		MachineInputBase.__init__(self)
		try:
			self.machine = machine_registry.get(machine_type)(machine_options)
			self.machine_type = machine_type
			self.machine_options = machine_options
			mappings = system.KEYMAPS.get(machine_type)
			self.machine.set_mappings(mappings)
		except NoSuchMachineException as e:
			raise InvalidConfigurationError(unicode(e))	
		
	def start_input(self, done):
		self.machine.add_stroke_callback(lambda keys: self._notify(' '.join(keys)))
		self.machine.start_capture()

	def stop_input(self):
		self.machine.stop_capture()
	
	def get_info(self):
		return "Input: Machine input \nMachine type: {}".format(self.machine_type)

	def __repr__(self):
		return "MachineInputPhysical(%s, %s)" % (self.machine_type, ",".join(self.machine_options))
		

class InputError(Exception):
	"""Exception raised for errors in the input."""

	def __init__(self, msg):
		self.value = msg