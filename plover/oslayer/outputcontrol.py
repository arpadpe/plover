#!/usr/bin/env python

import sys

#if sys.platform.startswith('linux'):
#    
#elif sys.platform.startswith('win32'):
#    
#elif sys.platform.startswith('darwin'):
#

if sys.platform.startswith('win32'):
	import winoutputhandler as outputhandler

class OutputHandler(outputhandler.OutputHandler):
	"""Choose output location from config"""
	pass
