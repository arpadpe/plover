import serial
from plover.exception import SerialPortException

class VirtualStenotypeBase(object):
	
	def __init__(self, *serial_params):
		self.serial_port = None
		self.serial_params = serial_params
		
	def start(self):
		if self.serial_port:
			self.serial_port.close()
			
		try:
			self.serial_port = serial.Serial(*self.serial_params)
		except (serial.SerialException, OSError, TypeError) as e:
			self._error("Could not start serial port")
			return
		if self.serial_port is None or not self.serial_port.isOpen():
			self._error("Could not start serial port")
			
	def stop(self):
		if self.serial_port:
			self.serial_port.close()
			
	def send(steno_key):
		pass

	def _error(self, msg):
		raise VirtualStenotypeError(msg)
		
class VirtualStenotypeError(Exception):
	"""Serial exception raised due to an error creating a serial socket."""

	def __init__(self, msg):
		self.value = msg