#!/usr/bin/env python

from Xlib import X, display
from plover.oslayer.xkeyboardcontrol import KeyboardEmulation

LINUX_DEFAULTS = ["Desktop", "Hud"]
DEFAULT_OUTPUT_WINDOW = 'Focus window'

def get_window_name(xid):
	window = display.Display().create_resource_object('window', xid)
	return window.get_wm_class()

def get_open_windows(self):
	windows = {DEFAULT_OUTPUT_WINDOW : lambda x : x = self.display.get_input_focus().focus}
	display = display.Display()
	win_list = display.screen().root.query_tree().children
	for win in win_list:
	    attrs = win.get_attributes()
	    if attrs.map_state == X.IsViewable:
	    	try:
	    		for child in win.query_tree().children:
	    			for grandchild in child.query_tree().children:
			    		classname = grandchild.get_wm_class()
			    		if grandchild is not None and classname is not None and classname not in LINUX_DEFAULTS:
			    			self.windows[classname] = grandchild.id
	    	except IndexError:
	    		# Thrown if a window doesn't have children
	    		pass

	return windows

def get_window_child_handles(self, windowname):
	# Not needed under linux
	return dict()

class OutputHandler(object):

	def __init__(self):
		self.keyboard_control = None
		self.display = display.Display()
	
	def send_backspaces(self, number_of_backspaces):
		if self.keyboard_control is not None:
			self.keyboard_control.send_backspaces(number_of_backspaces)

	def send_string(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control.send_string(s)

	def send_key_combination(self, s):
		if self.keyboard_control is not None:
			self.keyboard_control(s)

	def set_output_location(self, xid):
		if xid not in self.windows.values():
			return
		window = self.display.create_resource_object('window', int(xid))
		self.keyboard_control = KeyboardEmulation(window)
