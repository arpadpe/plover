#!/usr/bin/env python

from Xlib import X, display
from plover.oslayer.xkeyboardcontrol import KeyboardEmulation

LINUX_DEFAULTS = ["Desktop", "Hud"]
DEFAULT_OUTPUT_WINDOW = 'Focus window'

def get_window_name(xid):
	window = display.Display().create_resource_object('window', xid)
	return window.get_wm_class()

def get_open_windows():
	self_display = display.Display()
	windows = {DEFAULT_OUTPUT_WINDOW : lambda x : self_display.get_input_focus().focus}
	win_list = self_display.screen().root.query_tree().children
	for win in win_list:
	    attrs = win.get_attributes()
	    if attrs.map_state == X.IsViewable:
    		for child in win.query_tree().children:
    			for grandchild in child.query_tree().children:
		    		windowname = grandchild.get_wm_name()
		    		if grandchild is not None and windowname is not None and windowname not in LINUX_DEFAULTS:
		    			windows[windowname] = grandchild

	return windows

def get_window_child_handles(windowname):
	# Not needed under linux
	return dict()

def get_window_child_handles_for_pattern(windowname):
	# Not needed under linux
	return dict()

class OutputHandler(object):

	def __init__(self, backspace = True, handle_file = None):
		self.keyboard_control = None
		self.backspace = backspace
		self.display = display.Display()
	
	def send_backspaces(self, number_of_backspaces):
		if self.keyboard_control is not None:
			if self.backspace:
				self.keyboard_control.send_backspaces(number_of_backspaces)
			else:
				self.keyboard_control.send_string('*')

	def send_string(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control.send_string(s)

	def send_key_combination(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control.send_key_combination(s)

	def set_output_location(self, windowname):
		self.windows = get_open_windows()
		if windowname not in self.windows.keys():
			return False
		self.keyboard_control = KeyboardEmulation(self.windows[windowname])
		return True
