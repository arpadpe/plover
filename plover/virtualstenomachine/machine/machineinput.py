#!/usr/bin/env python

import os.path
import threading
from plover.machine.registry import machine_registry, NoSuchMachineException
from plover.virtualstenomachine.machine.machinenetwork import StenoMachineServer
from plover import system
import time

class MachineInputBase(object):
	"""The base class for stenotype machine input"""

	def __init__(self):
		self.subscribers = []
		
	def add_callback(self, callback):
		"""Subscribe to input."""
		
		self.subscribers.append(callback)

	def remove_callback(self, callback):
		"""Unsubscribe from input"""
		if callback in self.subscribers:
			self.subscribers.remove(callback)

	def start_input(self, done):
		"""Begin listening for input."""
		pass

	def stop_input(self):
		"""End listening for input."""
		pass
	
	def _notify(self, input):
		"""Invoke the callback of each subscriber with the given argument."""
		for callback in self.subscribers:
			callback(input)
			
	def get_info(self):
		return "Input:"
	
	def _error(self, msg):
		raise Exception(msg)

	def __repr__(self):
		return "MachineInputBase()"

class MachineInputFile(MachineInputBase):
	"""The file input class for stenotype machine input"""

	def __init__(self, filename, delimiter=None):
		if not os.path.isfile(filename):
			self._error("File not found")
		self.filename = filename
		self.delimiter = delimiter if delimiter is not None else '\n'
		MachineInputBase.__init__(self)	
		
	def start_input(self):
		try:
			self.file = open(self.filename, 'r')
		except Exception:
			self._error("File could not be opened")	

		# wait 1 second before reading the file
		time.sleep(1)

		for line in self.file:
			for outline in line.strip().split(self.delimiter):
				if outline:
					for input in outline.strip().split('/'):
						if input:
							self._notify(input)
					
	def stop_input(self):
		try:
			self.file.close()
		except Exception:
			# file could not be opened
			pass
	
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
		
	def start_input(self):
		self.server.start()
		
	def stop_input(self):
		try:
			self.server.stop()
		except Exception:
			# thrown if no server started
			pass
		
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
		
	def start_input(self):
		self.machine.add_stroke_callback(lambda keys: self._notify(' '.join(keys)))
		self.machine.start_capture()

	def stop_input(self):
		try:
			self.machine.stop_capture()
		except Exception as e:
			# thrown if no machine configured
			pass
	
	def get_info(self):
		if 'port' in self.machine_options:
			return "Input: Machine input \nMachine type: %s\nSerial Port: %s" % (self.machine_type, self.machine_options['port'])
		else:
			return "Input: Machine input \nMachine type: %s" % (self.machine_type)

	def __repr__(self):
		return "MachineInputPhysical(%s, %s)" % (self.machine_type, ",".join(self.machine_options))
		

class InputError(Exception):
	"""Exception raised for errors in the input."""

	def __init__(self, msg):
		self.value = msg