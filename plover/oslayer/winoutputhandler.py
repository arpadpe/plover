#!/usr/bin/env python

import re
import win32gui
import win32api
import win32con
import pywintypes
import win_window_handle_loader as loader

WINDOWS_DEFAULTS = ["Start", "Clock", "CPU Meter", "Program Manager"]
PLOVER_DEFAULTS = ["Plover: running", "Plover: stopped", "Plover: error", "Plover", "plover", "Plover Configuration"]
DEFAULT_OUTPUT_WINDOW = 'Focus window'

windows = {DEFAULT_OUTPUT_WINDOW : None}

def get_window_text(hwnd):
	return win32gui.GetWindowText(hwnd)

def get_window_class(hwnd):
	return win32gui.GetClassName(hwnd)

def get_open_windows():
	windows.clear()
	win32gui.EnumWindows(enumHandler, [windows, get_window_text])
	return windows

def get_window_child_handles(hwnd):
	if hwnd not in windows.values():
		return dict()
	handles = dict()
	try:
		handles[get_window_class(hwnd)] = hwnd
		win32gui.EnumChildWindows(hwnd, enumHandler, [handles, get_window_class])
	except Exception:
		# Thrown if no child windows present
		pass
	return handles

def get_window_child_handles_for_pattern(windowname):
	pattern = re.compile(re.escape(windowname), re.IGNORECASE)
	windows = get_open_windows()
	match = False
	handles = None
	for window, handle in windows.items():
		if pattern.search(window):
			if match:
				raise Exception('Multiple matches found, add specific window name')
			handles = get_window_child_handles(handle)
	if handles is None:
		raise Exception('No matches found, add window name or type handle')
	return handles

def get_all_handles():
	window_handles = dict()
	windows = get_open_windows()
	for window, handle in windows.items():
		handles = get_window_child_handles(handle)
		window_handles[window] = handles
	return window_handles

def get_handle_for_window(filename, window):
	window_handles = loader.load_window_handles(filename)
	if window in window_handles.keys():
		return window_handles[window]
	else:
		window_handles_regex = { re.compile(re.escape(key), re.IGNORECASE):value for key,value in window_handles.items() }
		for key, value in window_handles_regex.items():
			if key.search(window):
				return value
	return None


def window_found(windowname):
	pattern = re.compile(re.escape(windowname), re.IGNORECASE)
	windows = get_open_windows()
	match = False
	for window, handle in windows.items():
		if pattern.search(window):
			return True
	return False	

def send_test_text(hwnd=None, windowname=None, handlename=None, text='test'):
	if not hwnd:
		if not windowname:
			raise Exception('No window chosen')
		if not handlename:
			raise Exception('No handle chosen')
		if not window_found(windowname):
			raise Exception('Wndow not found')
		window_handles = get_window_child_handles_for_pattern(windowname)
		hwnd = window_handles[handlename]

	for char in text:
		win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)

def enumHandler(hwnd, lParam):
	dictionary = lParam[0]
	func = lParam[1]
	if win32gui.IsWindowVisible(hwnd):
		window = func(hwnd)
		if window is not '' and window not in PLOVER_DEFAULTS and window not in WINDOWS_DEFAULTS:
			dictionary[window] = hwnd
	return True

class OutputHandler(object):

	def __init__(self, backspace = True, handle_file = None):
		self.destinationHwnd = -1
		self.backspace = backspace
		self.handle_file = handle_file
		try:
			self.window_handles = loader.load_window_handles(handle_file)
			self.window_handles_regex = { re.compile(re.escape(key), re.IGNORECASE):value for key,value in self.window_handles.items() }
		except Exception as e:
			raise
	
	def send_backspaces(self, number_of_backspaces):
		if self.destinationHwnd < 0:
			return
		if self.backspace:
			for _ in xrange(number_of_backspaces):
				win32api.PostMessage(self.destinationHwnd, win32con.WM_CHAR, ord('\b'), 0)
		else:
			win32api.PostMessage(self.destinationHwnd, win32con.WM_CHAR, ord('*'), 0)

	def send_string(self, s):
		if self.destinationHwnd < 0:
			return
		for char in s:
			win32api.PostMessage(self.destinationHwnd, win32con.WM_CHAR, ord(char), 0)

	def send_key_combination(self, s):
		# Not supported
		pass

	def set_output_location(self, window):
		window_handles = get_all_handles()

		if window not in window_handles.keys():
			return False

		for key, value in self.window_handles_regex.items():
			if key.search(window):
				window_handle = value
				break

		try:
			self.destinationHwnd = window_handles[window][window_handle]
			return True
		except Exception as e:
			pattern = re.compile(re.escape(window_handle), re.IGNORECASE)
			for handle,hwnd in window_handles[window].values().items():
				if pattern.match(handle):
					self.destinationHwnd = hwnd
					return False

		return False
