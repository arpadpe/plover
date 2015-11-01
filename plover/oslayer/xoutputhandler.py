#!/usr/bin/env python

from Xlib import X, display
from plover.oslayer.xkeyboardcontrol import KeyboardEmulation

LINUX_DEFAULTS = ["Desktop", "Hud"]

class OutputHandler():

	def __init__(self):
		self.keyboard_control = None
		self.get_open_windows()
	
	def send_backspaces(self, number_of_backspaces):
		if self.keyboard_control is not None:
			self.keyboard_control.send_backspaces(number_of_backspaces)

	def send_string(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control.send_string(s)

	def send_key_combination(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control(s)

	def get_open_windows(self):
		# return dictionary - windowText,className
		self.windows = dict()
		self.display = display.Display()
		self.win_list = self.display.screen().root.query_tree().children
		for win in self.win_list:
		    attrs = win.get_attributes()
		    if attrs.map_state == X.IsViewable:
		    	try:
		    		name = win.query_tree().children[0].query_tree().children[0].get_wm_name()
		    		classname = win.query_tree().children[0].query_tree().children[0].get_wm_class()
		    		if name is not None and classname is not None and name not in LINUX_DEFAULTS:
		    			self.windows[name] = classname
		    	except IndexError:
		    		# Thrown if a window doesn't have children
		    		pass

		return self.windows

	def set_output_location(self, windowname):
		if windowname not in self.windows.keys():
			return
		self.keyboard_control = KeyboardEmulation(self.windows[windowname])
