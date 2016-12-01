

def get_window_name(window):
	return ''

def get_open_windows():
	return dict()

def get_window_child_handles(windowname):
	return dict()

def get_window_child_handles_for_pattern(windowname):
	return dict()

def window_found(windowname):
	return False

def send_test_text(hwnd=None, windowname=None, handlename=None, text='test'):
	pass

def get_handle_for_window(filename, window):
	return None


class OutputHandler(object):
	'''Default OutputHandler for OSX'''

	def __init__(self, backspace = True, handle_file = None):
		pass
	
	def send_backspaces(self, number_of_backspaces):
		pass

	def send_string(self, s):
		pass

	def send_key_combination(self, s):
		pass

	def set_output_location(self, windowname):
		return False