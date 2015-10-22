#!/usr/bin/env python

import win32gui
import win32api
import win32con

WINDOWS_DEFAULTS = ["Start", "Clock", "CPU Meter", "Program Manager"]
PLOVER_DEFAULTS = ["Plover: running", "Plover: stopped", "Plover: error"]

class OutputHandler():

	def __init__(self):
		self.windows = dict()
		self.get_open_windows()

	
	def send_backspaces(self, number_of_backspaces):
		if self.hwndEdit < 0:
			return
		for _ in xrange(number_of_backspaces):
			win32api.PostMessage(self.hwndEdit, win32con.WM_CHAR, ord('\b'), 0)

	def send_string(self, s):
		if self.hwndEdit < 0:
			return
		for char in s:
			win32api.PostMessage(self.hwndEdit, win32con.WM_CHAR, ord(char), 0)

	def send_key_combination(self, s):
		##
		pass

	def get_open_windows(self):
		self.windows = dict()
		win32gui.EnumWindows(self.enumHandler, None)
		return self.windows

	def enumHandler(self, hwnd, lParam):
		if win32gui.IsWindowVisible(hwnd):
			if win32gui.GetWindowText(hwnd) is not '' and win32gui.GetWindowText(hwnd) not in PLOVER_DEFAULTS and win32gui.GetWindowText(hwnd) not in WINDOWS_DEFAULTS:
				self.windows[win32gui.GetWindowText(hwnd)] = win32gui.GetClassName(hwnd)
	
	def child_windows(self, hwnd, lParam):
		if win32gui.IsWindowVisible(hwnd) and self.getHandle:
			self.hwndEdit = win32gui.FindWindowEx( win32gui.GetParent(hwnd), 0, win32gui.GetClassName(hwnd), None)
			self.getHandle = False
		return True

	def set_output_location(self, windowname):
		if windowname not in self.windows.keys():
			return
		self.windowname = windowname
		self.hwndMain = win32gui.FindWindow( self.windows[windowname], windowname)
		self.hwndEdit = win32gui.FindWindowEx( self.hwndMain, 0, None, None )
		self.getHandle = True
		win32gui.EnumChildWindows(self.hwndMain, self.child_windows, None)
		
