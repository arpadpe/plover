# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

"Thread-Based monitoring of a stenotype machine using the passport protocol."

import time
import plover.machine.passport as passport
from plover.virtualstenomachine.machine.base import VirtualStenotypeBase

# Passport protocol is documented here:
# http://www.eclipsecat.com/?q=system/files/Passport%20protocol_0.pdf

STENO_KEY_CHART = {
    'S-':'S',
    'T-':'T',
    'K-':'K',
    'P-':'P',
    'W-':'W',
    'H-':'H',
    'R-':'R',
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

DEFAULTS = ['#', '*']

SHADOW = 'f'

#STENO_KEY_CHART = {value : key for key, value in passport.STENO_KEY_CHART.items() if value}

class VirtualStenotypePassport(VirtualStenotypeBase):
	"""Passport interface."""

	def __init__(self, *params):
		VirtualStenotypeBase.__init__(self, *params)
		self.stroke_number = 0
		self.start_time = int(time.time())
		self.params = params

	def send(self, key_stroke):
		current_time = int(time.time())
		packet = ['<', str(self.stroke_number), '/']
		keys = key_stroke.split(' ')
		for key in keys:
			if self.get_stroke(key):
				packet.append(self.get_stroke(key))
				packet.append(SHADOW)
			else:
				index = 0
				for char in key:
					if char in DEFAULTS:
						packet.append(char)
						packet.append(SHADOW)
					elif index < len(key) / 2:
						if self.get_stroke(char + '-'):
							packet.append(self.get_stroke(char + '-'))
							packet.append(SHADOW)
						elif self.get_stroke('-' + char):
							packet.append(self.get_stroke('-' + char))
							packet.append(SHADOW)
						elif char != '/' and char in STENO_KEY_CHART.values():
							packet.append(char)
							packet.append(SHADOW)
					else:
						if self.get_stroke('-' + char):
							packet.append(self.get_stroke('-' + char))
							packet.append(SHADOW)
						elif self.get_stroke(char + '-'):
							packet.append(self.get_stroke(char + '-'))
							packet.append(SHADOW)
						elif char != '/' and char in STENO_KEY_CHART.values():
							packet.append(char)
							packet.append(SHADOW)
					index += 1

		packet.append('/')
		packet.append(str(self.start_time - current_time))
		packet.append('>')
		raw = ''.join(packet)
		self.serial_port.write(raw.encode('utf8'))
		self.serial_port.flush()
		del packet[:]
		self.stroke_number += 1

	def get_stroke(self, key):
		if key in STENO_KEY_CHART.keys():
			return STENO_KEY_CHART[key]
		else:
			return None

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