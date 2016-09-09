# Copyright (c) 2011 Hesky Fisher
# See LICENSE.txt for details.

"Thread-based monitoring of a stenotype machine using the TX Bolt protocol."

import plover.machine.txbolt as txbolt
from plover.virtualstenomachine.machine.base import VirtualStenotypeBase

# In the TX Bolt protocol, there are four sets of keys grouped in
# order from left to right. Each byte represents all the keys that
# were pressed in that set. The first two bits indicate which set this
# byte represents. The next bits are set if the corresponding key was
# pressed for the stroke.

# 00XXXXXX 01XXXXXX 10XXXXXX 110XXXXX
#   HWPKTS   UE*OAR   GLBPRF    #ZDST

# The protocol uses variable length packets of one, two, three or four
# bytes. Only those bytes for which keys were pressed will be
# transmitted. The bytes arrive in order of the sets so it is clear
# when a new stroke starts. Also, if a key is pressed in an earlier
# set in one stroke and then a key is pressed only in a later set then
# there will be a zero byte to indicate that this is a new stroke. So,
# it is reliable to assume that a stroke ended when a lower set is
# seen. Additionally, if there is no activity then the machine will
# send a zero byte every few seconds.

STENO_KEY_CHART = ("S-", "T-", "K-", "P-", "W-", "H-",  # 00
                   "R-", "A-", "O-", "*", "-E", "-U",   # 01
                   "-F", "-R", "-P", "-B", "-L", "-G",  # 10
                   "-T", "-S", "-D", "-Z", "#")         # 11


class VirtualStenotype(VirtualStenotypeBase):
	"""TX Bolt interface.

	This class implements the three methods necessary for a standard
	stenotype interface: start_capture, stop_capture, and
	add_callback.

	"""
	def send(self, key_stroke):
		keys = key_stroke.split(' ')
		key_sets = [0,0,0,0]
		for key in keys:
			index = STENO_KEY_CHART.index(key)
			key_set, key_index = divmod(index, 6)
			key_code = (key_set << 6) | (1 << key_index)
			key_sets[key_set] |= key_code
		
		for key_set in key_sets:
			if key_set > 0:
				self.serial_port.write(chr(key_set))
		self.serial_port.write(chr(0))
		
		del key_sets[:]
