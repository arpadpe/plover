#!/usr/bin/env python

import sys

if sys.platform.startswith('win32'):
	import winoutputhandler as outputhandler
elif sys.platform.startswith('linux'):
	import xoutputhandler as outputhandler
elif sys.platform.startswith('darwin'):
	import osxoutputhandler as outputhandler

class OutputHandler(outputhandler.OutputHandler):
	"""Choose output location from config"""
	pass


def get_window_name(window):
	return outputhandler.get_window_name(window)

def get_open_windows():
	return outputhandler.get_open_windows()

def get_window_child_handles(windowname):
	return outputhandler.get_window_child_handles(windowname)

def get_window_child_handles_for_pattern(windowname):
	return outputhandler.get_window_child_handles_for_pattern(windowname)

def window_found(windowname):
	return outputhandler.window_found(windowname)

def send_test_text(hwnd=None, windowname=None, handlename=None, text='test'):
	outputhandler.send_test_text(hwnd, windowname, handlename, text)

def get_handle_for_window(filename, window):
	return outputhandler.get_handle_for_window(filename, window)

def get_handle_needed():
	if sys.platform.startswith('win32'):
		return True
	elif sys.platform.startswith('linux'):
		return False
	elif sys.platform.startswith('darwin'):
		return False
	