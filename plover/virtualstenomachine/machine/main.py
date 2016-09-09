#!/usr/bin/env python

print 0b10
print bin(0x80)
for j in range(1, 8):
	print bin(0x80 >> j)

STENO_KEY_CHART = ("S-", "T-", "K-", "P-", "W-", "H-",  # 00
                   "R-", "A-", "O-", "*", "-E", "-U",   # 01
                   "-F", "-R", "-P", "-B", "-L", "-G",  # 10
                   "-T", "-S", "-D", "-Z", "#")			# 11


a = 6 >> 2
#print bin(6 << 2)
#print a

#print int(0b0)
#print int(0b11111111 >> 8) 

index = STENO_KEY_CHART.index("-D")
key_set, key_index = divmod(index, 6)

#print bin(key_set << 6)
#print bin(key_index)
#print bin(key_set << 6 | 1 << key_index

key_sets = [0,0,0,0]
key_code = (key_set << 6) | (1 << key_index)
key_sets[key_set] |= key_code

index = STENO_KEY_CHART.index("-B")
key_set, key_index = divmod(index, 6)
key_code = (key_set << 6) | (1 << key_index)
key_sets[key_set] |= key_code



index = STENO_KEY_CHART.index("-E")
key_set, key_index = divmod(index, 6)
key_code = (key_set << 6) | (1 << key_index)
key_sets[key_set] |= key_code

index = STENO_KEY_CHART.index("*")
key_set, key_index = divmod(index, 6)
key_code = (key_set << 6) | (1 << key_index)
key_sets[key_set] |= key_code

'''
STENO_KEY_CHART = {
    '!': None,
    '#': '#',
    '^': None,
    '+': None,
    'S': 'S-',
    'C': 'S-',
    'T': 'T-',
    'K': 'K-',
    'P': 'P-',
    'W': 'W-',
    'H': 'H-',
    'R': 'R-',
    '~': '*',
    '*': '*',
    'A': 'A-',
    'O': 'O-',
    'E': '-E',
    'U': '-U',
    'F': '-F',
    'Q': '-R',
    'N': '-P',
    'B': '-B',
    'L': '-L',
    'G': '-G',
    'Y': '-T',
    'X': '-S',
    'D': '-D',
    'Z': '-Z',
}

print STENO_KEY_CHART

#for key,value in STENO_KEY_CHART.items():
#	print key,value

chart = {value : key for key, value in STENO_KEY_CHART.items() if value}
print chart
'''
"""
def printinput(string):
	print string

#server = StenoMachineServer(machinenetwork.DEFAULT_HOST, machinenetwork.DEFAULT_PORT, printinput)
#server.start()

input = Input("NKRO Keyboard")
input.add_callback(printinput)
input.start_input()
while 1:
	text = raw_input('Enter your input:')
	if text == "exit":
		input.stop_input()
#input.stop_input()
"""

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