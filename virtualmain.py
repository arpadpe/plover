#!/usr/bin/env python

STENO_KEY_CHART = ('^', '#', 'S-', 'T-', 'K-', 'P-',    
                    'W-', 'H-', 'R-', 'A-', 'O-', '*',   
                    '-E', '-U', '-F', '-R', '-P', '-B',  
                    '-L', '-G', '-T', '-S', '-D', '-Z')  

'''
from plover.virtualstenomachine.machine.geminipr import VirtualStenotype

machine = VirtualStenotype('COM1')

machine.start()

machine.send("S-")
machine.send("K- -G")
machine.send("-U -Z")
machine.send("# P- -R -D")
machine.send("A- O- -L")
machine.send("S- T- K- P- -E -B -S")

machine.stop()
'''
'''
from plover.virtualstenomachine.machine.passport import VirtualStenotype

machine = VirtualStenotype('COM1', 38400)

machine.start()

machine.send("S-")
machine.send("K- -G")
machine.send("-U -Z")
machine.send("# P- -R -D")
machine.send("A- O- -L")
machine.send("S- T- K- P- -E -B -S")

machine.stop()
'''
'''
from plover.virtualstenomachine.machine.stentura import VirtualStenotype

machine = VirtualStenotype('COM1')

machine.start()

machine.send("S-")
machine.send("K- -G")
machine.send("-U -Z")
machine.send("# P- -R -D")
machine.send("A- O- -L")
machine.send("S- T- K- P- -E -B -S")

machine.stop()


from plover.virtualstenomachine.machine.txbolt import VirtualStenotype

machine = VirtualStenotype('COM1')

machine.start()

machine.send("S-")
machine.send("K- -G")
machine.send("-U -Z")
machine.send("# P- -R -D")
machine.send("A- O- -L")
machine.send("S- T- K- P- -E -B -S")

machine.stop()
'''

import os
import shutil
import sys
import traceback

WXVER = '2.8'
if not hasattr(sys, 'frozen'):
    import wxversion
    wxversion.ensureMinimal(WXVER)

import wx
import json
import glob
from plover.virtualstenomachine.gui.main import VirtualMachineGUI
from plover.oslayer.config import CONFIG_DIR, ASSETS_DIR
from plover.config import CONFIG_FILE, Config
# DEFAULT_DICTIONARY_FILE, 

def show_error(title, message):
	"""Report error to the user.

	This shows a graphical error and prints the same to the terminal.
	"""
	print message
	app = wx.PySimpleApp()
	alert_dialog = wx.MessageDialog(None,
									message,
									title,
									wx.OK | wx.ICON_INFORMATION)
	alert_dialog.ShowModal()
	alert_dialog.Destroy()

def init_config_dir():
	"""Creates plover's config dir.

	This usually only does anything the first time plover is launched.
	"""
	# Create the configuration directory if needed.
	if not os.path.exists(CONFIG_DIR):
		os.makedirs(CONFIG_DIR)

	# Copy the default dictionary to the configuration directory.
	if not os.path.exists(CONFIG_DIR):
		unified_dict = {}
		dict_filenames = glob.glob(os.path.join(ASSETS_DIR, '*.json'))
		for dict_filename in dict_filenames:
			unified_dict.update(json.load(open(dict_filename, 'rb')))
			ordered = OrderedDict(sorted(unified_dict.iteritems(), key=lambda x: x[1]))
			outfile = open(CONFIG_DIR, 'wb')
			json.dump(ordered, outfile, indent=0, separators=(',', ': '))

	# Create a default configuration file if one doesn't already
	# exist.
	if not os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'wb') as f:
			f.close()

def main():
	"""Launch VirtualStenoMachine."""
	try:
		init_config_dir()
		config = Config()
		config.target_file = CONFIG_FILE
		gui = VirtualMachineGUI(config)
		gui.MainLoop()
	except:
		show_error('Unexpected error', traceback.format_exc())
	os._exit(1)

if __name__ == '__main__':
    main()

'''
from plover.virtualstenomachine.machine.machineinput import MachineInputPhysical as Input
import plover.virtualstenomachine.machine.machineinput
from plover.machine.keymap import Keymap
from plover.oslayer.keyboardcontrol import KeyboardCapture


def printinput(string):
	print string

#server = StenoMachineServer(machinenetwork.DEFAULT_HOST, machinenetwork.DEFAULT_PORT, printinput)
#server.start()

input = Input("NKRO Keyboard", {'arpeggiate' : False, 'keymap' : Keymap.default() } )
input.add_callback(printinput)
input.start_input()
try:
	while True:
		pass
except KeyboardInterrupt:
	input.stop_input()
#input.stop_input()
'''
'''
kc = KeyboardCapture()

def test(event):
	print event.keystring

kc.key_up = test
kc.start()
print 'Press CTRL-c to quit.'
try:
	while True:
		pass
except KeyboardInterrupt:
	kc.cancel()
'''
'''
try:
	input = Input('input.txt')
except machineinput.InputError as e:
	print e.value

def printinput(string):
	print string
	
input.add_callback(printinput)

input.start_input()
'''