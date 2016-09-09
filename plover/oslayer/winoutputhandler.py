#!/usr/bin/env python

import re
import win32gui
import win32api
import win32con
import pywinauto
import pywintypes
from pywinauto import Application
from winkeyboardcontrol import KeyboardEmulation

WINDOWS_DEFAULTS = ["Start", "Clock", "CPU Meter", "Program Manager"]
PLOVER_DEFAULTS = ["Plover: running", "Plover: stopped", "Plover: error", "plover"]
DEFAULT_OUTPUT_WINDOW = 'Focus window'

windows = {DEFAULT_OUTPUT_WINDOW : None}

def get_window_text(hwnd):
	return win32gui.GetWindowText(hwnd)

def get_window_class(hwnd):
	return win32gui.GetClassName(hwnd)

def get_open_windows():
	win32gui.EnumWindows(enumHandler, [windows, get_window_text])
	print windows
	return windows

def get_window_child_handles(hwnd):
	if hwnd not in windows.values():
		return dict()
	handles = dict()
	try:
		handles[get_window_class(hwnd)] = hwnd
		win32gui.EnumChildWindows(hwnd, enumHandler, [handles, get_window_class])
	except pywintypes.error:
		# Thrown if no child windows present
		pass
	print handles
	return handles

def get_all_handles():
	window_handles = dict()
	windows = get_open_windows()
	for window, handle in windows.items():
		handles = get_window_child_handles(handle)
		window_handles[window] = handles

def enumHandler(hwnd, lParam):
	dictionary = lParam[0]
	func = lParam[1]
	if win32gui.IsWindowVisible(hwnd):
		window = func(hwnd)
		if window is not '' and window not in PLOVER_DEFAULTS and window not in WINDOWS_DEFAULTS:
			dictionary[window] = hwnd
	return True

class OutputHandler():

	def __init__(self):
		self.destinationHwnd = -1
	
	def send_backspaces(self, number_of_backspaces):
		if self.destinationHwnd < 0:
			return
		for _ in xrange(number_of_backspaces):
			win32api.PostMessage(self.destinationHwnd, win32con.WM_CHAR, ord('\b'), 0)

	def send_string(self, s):
		print self.destinationHwnd
		if self.destinationHwnd < 0:
			return
		for char in s:
			print win32api.PostMessage(self.destinationHwnd, win32con.WM_CHAR, ord(char), 0)

	def send_key_combination(self, s):
		# Not supported
		pass

	def set_output_location(self, handle_class):
		window_handles = get_all_handles()
		for window, handles in window_handles.items():
			if handle_class in handles.keys():
				self.destinationHwnd = handles[handle_class]
				continue
		#print get_window_class(handle)
		#self.destinationHwnd = int(window)
