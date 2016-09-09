#!/usr/bin/env python

import sys

if sys.platform.startswith('win32'):
	import winoutputhandler as outputhandler
elif sys.platform.startswith('linux'):
	import xoutputhandler as outputhandler
elif sys.platform.startswith('darwin'):
	# TODO
	pass

class OutputHandler(outputhandler.OutputHandler):
	"""Choose output location from config"""
	pass


def get_window_name(window):
	return outputhandler.get_window_name(window)

def get_open_windows():
	return outputhandler.get_open_windows()

def get_window_child_handles(windowname):
	return outputhandler.get_window_child_handles(windowname)
