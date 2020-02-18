#!/usr/bin/env python

from plover.virtualstenomachine.machine.machineinput import MachineInputBase
from plover.virtualstenomachine.machine.machineinput import MachineInputFile
from plover.virtualstenomachine.machine.machineinput import MachineInputNetwork
from plover.virtualstenomachine.machine.machineinput import MachineInputPhysical

from plover.virtualstenomachine.machine.machineoutput import MachineOutputBase
from plover.virtualstenomachine.machine.machineoutput import MachineOutputSerial
from plover.virtualstenomachine.machine.machineoutput import MachineOutputNetwork

MACHINE_INPUT_FILE = "File input"
MACHINE_INPUT_NETWORK = "Network input"
MACHINE_INPUT_PHYSICAL = "Physcal machine input"

MACHINE_OUTPUT_SERIAL = "Serial output"
MACHINE_OUTPUT_NETWORK = "Network output"

class VirtualStenotypeMachine(object):
	"""The main class for virtual stenotype machine"""

	def __init__(self):
		self.input = MachineInputBase()
		self.output = MachineOutputBase()
		self.input_type = None
		self.input_params = dict()
		self.output_type = None
		self.output_params = dict()
		
	def set_input_type(self, input_type, params):
		if input_type == MACHINE_INPUT_FILE:
			self.input = MachineInputFile(params['filename'], params['delimiter'])
		elif input_type == MACHINE_INPUT_NETWORK:
			self.input = MachineInputNetwork(params['host'], params['port'])
		elif input_type == MACHINE_INPUT_PHYSICAL:
			self.input = MachineInputPhysical(params['machine_type'], params['machine_options'])
		self.input_type = input_type
		self.input_params = params
			
	def set_output_type(self, output_type, params):
		if output_type == MACHINE_OUTPUT_SERIAL:
			self.output = MachineOutputSerial(params['machine_type'], params['machine_options'])
		elif output_type == MACHINE_OUTPUT_NETWORK:
			self.output = MachineOutputNetwork(params['host'], params['port'])
		self.output_type = output_type
		self.output_params = params

	def start(self):
		self.input.add_callback(self.forward)
		self.output.start()
		self.input.start_input()
		
	def stop(self):
		if self.input:
			self.input.stop_input()
			self.input.remove_callback(self.forward)
		if self.output:
			self.output.stop()
		
	def forward(self, input):
		self.output.send(input)
		
	def get_input_types(self):
		return [MACHINE_INPUT_FILE, MACHINE_INPUT_NETWORK, MACHINE_INPUT_PHYSICAL]
		
	def get_output_types(self):
		return [MACHINE_OUTPUT_SERIAL, MACHINE_OUTPUT_NETWORK]
		
	def get_input_type(self):
		return self.input_type
		
	def get_input_params(self):
		return self.input_params
		
	def get_output_type(self):
		return self.output_type
		
	def get_output_params(self):
		return self.output_params
		
	def get_input_info(self):
		return self.input.get_info()
		
	def get_output_info(self):
		return self.output.get_info()
		
	def get_serial_output_types(self):
		return ['Gemini PR', 'Passport', 'Stentura', 'TX Bolt']

	def __str__(self):
		return "VirtualStenotypeMachine: %s %s" % (self.input, self.output)
		