
import plover.machine.geminipr as geminipr
from plover.virtualstenomachine.machine.base import VirtualStenotypeBase

# In the Gemini PR protocol, each packet consists of exactly six bytes
# and the most significant bit (MSB) of every byte is used exclusively
# to indicate whether that byte is the first byte of the packet
# (MSB=1) or one of the remaining five bytes of the packet (MSB=0). As
# such, there are really only seven bits of steno data in each packet
# byte. This is why the STENO_KEY_CHART below is visually presented as
# six rows of seven elements instead of six rows of eight elements.

STENO_KEY_CHART = ("Fn", "#", "#", "#", "#", "#", "#",
                   "S-", "S-", "T-", "K-", "P-", "W-", "H-",
                   "R-", "A-", "O-", "*", "*", "res", "res",
                   "pwr", "*", "*", "-E", "-U", "-F", "-R",
                   "-P", "-B", "-L", "-G", "-T", "-S", "-D",
                   "#", "#", "#", "#", "#", "#", "-Z")

BYTES_PER_STROKE = 6


class VirtualStenotypeGeminiPr(VirtualStenotypeBase):
	"""Standard stenotype interface for a Gemini PR machine.

	This class implements the send method.

	"""

	def send(self, key_stroke):
		"""Overrides base class run method. Do not call directly."""

		self.key_sets = [ 0x80, 0, 0, 0, 0, 0]
		keys = key_stroke.split(' ')
		for key in keys:

			if self._add_to_key_sets(key):
				continue

			char_index = -1
			for char in key:
				char_index += 1
				if char in STENO_KEY_CHART:
					self._add_to_key_sets(char)
				elif char_index < len(key) / 2:
					if self._add_to_key_sets(char + '-'):
						continue
					elif self._add_to_key_sets('-' + char):
						continue
				else:
					if self._add_to_key_sets('-' + char):
						continue
					elif self._add_to_key_sets(char + '-'):
						continue

		packet = chr(self.key_sets[0])
		for i in range(1,6):
			packet += chr(self.key_sets[i])
		self.serial_port.write(packet)
		
		del self.key_sets[:]

	def _add_to_key_sets(self, key):
		if key not in STENO_KEY_CHART:
			return False
		index = STENO_KEY_CHART.index(key)
		key_set, key_index = divmod(index, 7)
		key_code = 1 << 6 - key_index
		self.key_sets[key_set] |= key_code
		return True

	def __repr__(self):
		return "VirtualStenotypeGeminiPr(%s)" % self.serial_params
			