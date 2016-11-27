# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

"Thread-based monitoring of a stenotype machine using the passport protocol."

import time
import plover.machine.passport as passport
from plover.virtualstenomachine.machine.base import VirtualStenotypeBase

# Passport protocol is documented here:
# http://www.eclipsecat.com/?q=system/files/Passport%20protocol_0.pdf

STENO_KEY_CHART = {
    '#': '#',
    'S-': 'S',
    'S-':'C',
    'T-':'T',
    'K-':'K',
    'P-':'P',
    'W-':'W',
    'H-':'H',
    'R-':'R',
    '*':'*',
    'A-':'A',
    'O-':'O',
    '-E':'E',
    '-U':'U',
    '-F':'F',
    '-R':'Q',
    '-P':'N',
    '-B':'B',
    '-L':'L',
    '-G':'G',
    '-T':'Y',
    '-S':'X',
    '-D':'D',
    '-Z':'Z'
}

#STENO_KEY_CHART = {value : key for key, value in passport.STENO_KEY_CHART.items() if value}

class VirtualStenotypePassport(VirtualStenotypeBase):
	"""Passport interface."""

	def __init__(self, *params):
		VirtualStenotypeBase.__init__(self, *params)
		self.stroke_number = 0
		self.start_time = int(time.time())
		self.params = params

	def send(self, key_stroke):
		keys = key_stroke.split(' ')
		current_time = int(time.time())
		packet = ['<', str(self.stroke_number), '/']
		for key in keys:
			try:
				stroke = STENO_KEY_CHART[key]
			except:
				stroke = key
			packet.append(stroke)
			packet.append('f')
		packet.append('/')
		packet.append(str(self.start_time - current_time))
		packet.append('>')
		raw = ''.join(packet)
		self.serial_port.write(raw)
		self.serial_port.flush()
		del packet[:]
		self.stroke_number += 1

	@staticmethod
	def get_option_info():
		"""Get the default options for this machine."""
		bool_converter = lambda s: s == 'True'
		sb = lambda s: int(float(s)) if float(s).is_integer() else float(s)
		return {
			'port': (None, str), # TODO: make first port default
			'baudrate': (38400, int),
			'bytesize': (8, int),
			'parity': ('N', str),
			'stopbits': (1, sb),
			'timeout': (2.0, float),
			'xonxoff': (False, bool_converter),
			'rtscts': (False, bool_converter)
		}

	def __repr__(self):
		return "VirtualStenotypePassport(%s)" % self.params