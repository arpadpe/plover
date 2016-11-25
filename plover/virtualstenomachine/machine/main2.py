#!/usr/bin/env python

from machineinput import MachineInputFile as Input
import machineinput
from machinenetwork import StenoMachineClient
import machinenetwork

def printinput(string):
	print string

client = StenoMachineClient(machinenetwork.DEFAULT_HOST, machinenetwork.DEFAULT_PORT)

client.send("alma")


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