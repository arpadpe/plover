#!/usr/bin/env python

import wx
import wx.animate
from wx.lib.utils import AdjustRectToScreen
import wx.lib.filebrowsebutton as filebrowse
import plover.virtualstenomachine.machine.virtualmachine as virtualmachine
import plover.virtualstenomachine.machine.machinenetwork as machinenetwork
import plover.virtualstenomachine.machine.machineserial as machineserial
from plover.virtualstenomachine.machine.virtualmachine import VirtualStenotypeMachine
from plover.virtualstenomachine.machine.machineinput import InputError
from plover.machine.registry import machine_registry
from plover.gui.serial_config import SerialConfigDialog
from plover.gui.keyboard_config import KeyboardConfigDialog
from plover.machine.base import SerialStenotypeBase
from plover.gui.config import ConfigurationDialog

UI_BORDER = 4
ERROR_DIALOG_TITLE = "Error"
ALERT_DIALOG_TITLE = "Alert"
CONFIG_PANEL_SIZE = (-1, -1)
SAVE_CONFIG_BUTTON_NAME = "Choose"
CONFIG_BUTTON_NAME = "Config"
SERIAL_CONFIG_BUTTON_NAME = "Virtual Serial Config"

class VirtualMachineGUI(wx.App):
	"""The main entry point for the virtual steno machine application."""

	def __init__(self, config):
		self.config = config
		wx.App.__init__(self, redirect=False)

	def OnInit(self):
		"""Called just before the application starts."""
		frame = MainFrame(self.config)
		self.SetTopWindow(frame)
		frame.Show()
		return True
		
class MainFrame(wx.Frame):
	"""The top-level GUI element of the virtual steno machine application."""

	# Class constants.
	TITLE = "Virtual Steno Machine"
	ALERT_DIALOG_TITLE = TITLE
	BORDER = 5
	CONFIG_BUTTON_BORDER = 200
	START_BUTTON_LABEL = "Start"
	STOP_BUTTON_LABEL = "Stop"
	CONFIGURE_INPUT_BUTTON_LABEL = "Configure Input"
	CONFIGURE_OUTPUT_BUTTON_LABEL = "Configure Output"
	INPUT_TEXT_DEFAULT = "Input:"
	OUTPUT_TEXT_DEFAULT = "Output:"

	def __init__(self, config):
		wx.Frame.__init__(self, None, title=self.TITLE, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))				  
		self.config = config
		self.SetBackgroundColour('white')
		
		# Start button.
		self.start_button = wx.Button(self, label=self.START_BUTTON_LABEL)
		self.start_button.Bind(wx.EVT_BUTTON, self._start_machine)
		self.start_button.Disable()
		
		# Stop button.
		self.stop_button = wx.Button(self, label=self.STOP_BUTTON_LABEL)
		self.stop_button.Bind(wx.EVT_BUTTON, self._stop_machine)
		self.stop_button.Disable()
		
		# Input config button
		self.input_cfg_button = wx.Button(self, label=self.CONFIGURE_INPUT_BUTTON_LABEL)
		self.input_cfg_button.Bind(wx.EVT_BUTTON, self._show_input_configuration)
		
		# Output config button
		self.output_cfg_button = wx.Button(self, label=self.CONFIGURE_OUTPUT_BUTTON_LABEL)
		self.output_cfg_button.Bind(wx.EVT_BUTTON, self._show_output_configuration)
		
		self.machine = VirtualStenotypeMachine()
		
		# Layout.
		global_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.input_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.input_info = wx.StaticText(self, label=self.machine.get_input_info())
		self.input_sizer.Add(self.input_info)
		
		global_sizer.Add(self.input_sizer)
		
		global_sizer.Add(self.input_cfg_button, flag=wx.LEFT, border=self.CONFIG_BUTTON_BORDER)
		
		self.output_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.output_info = wx.StaticText(self, label=self.machine.get_output_info())
		self.output_sizer.Add(self.output_info)
		
		global_sizer.Add(self.output_sizer)
		
		global_sizer.Add(self.output_cfg_button, flag=wx.LEFT, border=self.CONFIG_BUTTON_BORDER)
		
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.start_button, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=self.BORDER)
		sizer.Add(self.stop_button, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=self.BORDER)
		global_sizer.Add(sizer)
		self.SetSizer(global_sizer)
		global_sizer.Fit(self)

		self.Bind(wx.EVT_CLOSE, self._quit)
		
		rect = wx.Rect(600, 400, *self.GetSize())
		self.SetRect(AdjustRectToScreen(rect))

	def _quit(self, event=None):
		if self.machine:
			self.machine.stop()
		self.Destroy()

	def _update(self):
		self.input_sizer.DeleteWindows()
		
		input_info_text = self.machine.get_input_info()
		self.input_info = wx.StaticText(self, label=input_info_text)
		self.input_sizer.Add(self.input_info)
		
		self.output_sizer.DeleteWindows()
		
		output_info_text = self.machine.get_output_info()
		self.output_info = wx.StaticText(self, label=output_info_text)
		self.output_sizer.Add(self.output_info)

		if (input_info_text != self.INPUT_TEXT_DEFAULT) and (output_info_text != self.OUTPUT_TEXT_DEFAULT):
			self.start_button.Enable()
			self.input_cfg_button.Enable()
			self.output_cfg_button.Enable()
		else:
			self.start_button.Disable()
			self.stop_button.Disable()
			
		self.GetSizer().Layout()
		self.GetSizer().Fit(self)
		
	def _start_machine(self, event=None):
		"""Called when the start button is clicked."""

		try:
			self.machine.start()
			self.start_button.Disable()
			self.input_cfg_button.Disable()
			self.output_cfg_button.Disable()
			self.stop_button.Enable()
		except Exception as e:
			self._show_alert(unicode(e))
		
	def _stop_machine(self, event=None):
		"""Called when the stop button is clicked."""
		if self.machine:
			self.machine.stop()
			self.start_button.Enable()
			self.input_cfg_button.Enable()
			self.output_cfg_button.Enable()
			self.stop_button.Disable()
		
	def _show_input_configuration(self, event=None):
		dlg = InputConfigurationDialog(self.machine, self.config, parent=self)
		dlg.Show()
		
	def _show_output_configuration(self, event=None):
		dlg = OutputConfigurationDialog(self.machine, self.config, parent=self)
		dlg.Show()		

	def _show_alert(self, message):
		alert_dialog = wx.MessageDialog(self, message, self.ALERT_DIALOG_TITLE, wx.OK | wx.ICON_INFORMATION)
		alert_dialog.ShowModal()
		alert_dialog.Destroy()

class InputConfigurationDialog(wx.Dialog):
	"""A GUI for viewing and editing Plover configuration files.

	Changes to the configuration file are saved when the GUI is closed. Changes
	will take effect the next time the configuration file is read by the
	application, which is typically after an application restart.

	"""

	CONFIGURATION_TITLE = "Virtual Stenotype Input Configuration"

	other_instances = []
	
	def __init__(self, machine, config, parent):
		"""Create a configuration GUI based on the given config file.

		Arguments:

		configuration file to view and edit.
		during_plover_init -- If this is set to True, the configuration dialog
		won't tell the user that Plover needs to be restarted.
		"""

		pos = (400, 400)
		size = wx.Size(400, 200)
		wx.Dialog.__init__(self, parent, title=self.CONFIGURATION_TITLE, pos=pos, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.machine = machine
		self.parent = parent
		self.config = config
		self.machine_params = None

		# Close all other instances.
		if self.other_instances:
			for instance in self.other_instances:
				instance.Close()
		del self.other_instances[:]
		
		self.other_instances.append(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(wx.StaticText(self, label="Input type: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
		
		input_types = self.machine.get_input_types()
		
		self.input_type_choice = wx.Choice(self, choices=input_types)
		self.Bind(wx.EVT_CHOICE, self._update, self.input_type_choice)
		box.Add(self.input_type_choice, proportion=1, flag=wx.EXPAND)
		sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
		
		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		sizer.Layout()
		self._update()

		self.SetRect(AdjustRectToScreen(self.GetRect()))

		self.Bind(wx.EVT_CLOSE, self.on_close)

	def on_close(self, event):
		try:
			self.other_instances.remove(self)
		except Exception:
			# thrown when no other instances
			pass
		self.parent._update()
		event.Skip()	

	def _update(self, event=None):
		# Refreshes the UI to reflect current data.
		input_type = self.machine.get_input_type()
		if (event or not input_type) and self.input_type_choice.GetStringSelection():
			input_type = self.input_type_choice.GetStringSelection()
		sizer = self.GetSizer()
		
		if len(sizer.GetChildren()) > 1:
			sizer.DeleteWindows()
			
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="Input type: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			input_types = self.machine.get_input_types()
			self.input_type_choice = wx.Choice(self, choices=input_types)
			self.Bind(wx.EVT_CHOICE, self._update, self.input_type_choice)
			box.Add(self.input_type_choice, proportion=1, flag=wx.EXPAND)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
		
		if input_type == virtualmachine.MACHINE_INPUT_FILE:
			self.input_type_choice.SetStringSelection(input_type)
			box = wx.BoxSizer(wx.HORIZONTAL)
			self.file_browser = filebrowse.FileBrowseButton( self, fileMode=wx.OPEN)
			if 'filename' in self.machine.get_input_params():
				self.file_browser.SetValue(self.machine.get_input_params()['filename'])
			box.Add(self.file_browser, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="File delimiter: "), border=UI_BORDER, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
			self.delimiter_textctrl = wx.TextCtrl(self)
			if 'delimiter' in self.machine.get_input_params():
				self.delimiter_textctrl.SetValue(self.machine.get_input_params()['delimiter'])
			else:
				self.delimiter_textctrl.SetValue(';')
			box.Add(self.delimiter_textctrl, border=UI_BORDER)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)

			button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME) 
			self.Bind(wx.EVT_BUTTON, self._file_input, button)
			sizer.Add(button, flag=wx.ALIGN_RIGHT)
			
		elif input_type == virtualmachine.MACHINE_INPUT_NETWORK:
			self.input_type_choice.SetStringSelection(input_type)
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="HOST: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			self.host_textctrl = wx.TextCtrl(self)
			if 'host' in self.machine.get_input_params():
				self.host_textctrl.SetValue(self.machine.get_input_params()['host'])
			else:
				self.host_textctrl.SetValue(machinenetwork.DEFAULT_HOST)
			box.Add(self.host_textctrl)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="PORT: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			self.port_textctrl = wx.TextCtrl(self)
			if 'port' in self.machine.get_input_params():
				self.port_textctrl.SetValue(str(self.machine.get_input_params()['port']))
			else:
				self.port_textctrl.SetValue(str(machinenetwork.DEFAULT_PORT))
			box.Add(self.port_textctrl)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			
			button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME)
			self.Bind(wx.EVT_BUTTON, self._network_input, button)
			sizer.Add(button, flag=wx.ALIGN_RIGHT)
			
		elif input_type == virtualmachine.MACHINE_INPUT_PHYSICAL:
			self.input_type_choice.SetStringSelection(input_type)
			box = wx.BoxSizer(wx.HORIZONTAL)			
			machines = machine_registry.get_all_names()
			self.machine_choice = wx.Choice(self, choices=machines)
			if 'machine_type' in self.machine.get_input_params():
				self.machine_choice.SetStringSelection(self.machine.get_input_params()['machine_type'])
			if 'machine_options' in self.machine.get_input_params():
				self.machine_params = self.machine.get_input_params()['machine_options']
			box.Add(self.machine_choice, proportion=1, flag=wx.EXPAND)			
			self.config_button = wx.Button(self, id=wx.ID_PREFERENCES, label=CONFIG_BUTTON_NAME)
			box.Add(self.config_button)
			self.Bind(wx.EVT_BUTTON, self._advanced_config, self.config_button)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME) 
			self.Bind(wx.EVT_BUTTON, self._physical_input, button)
			sizer.Add(button, flag=wx.ALIGN_RIGHT)
			
		sizer.Layout()
		
	def _file_input(self, event=None):
		filename = self.file_browser.GetValue()
		delimiter = self.delimiter_textctrl.GetValue()
		try:
			self.machine.set_input_type(virtualmachine.MACHINE_INPUT_FILE, { 'filename' : filename, 'delimiter' : delimiter})
			if self.IsModal():
				self.EndModal(wx.ID_SAVE)
			else:
				self.Close()
		except InputError as e:
			self._show_error_alert(e.value)
	
	def _network_input(self, event=None):
		try:
			self.machine.set_input_type(virtualmachine.MACHINE_INPUT_NETWORK, { 'host' : self.host_textctrl.GetValue(), 'port' : int(self.port_textctrl.GetValue())})
			if self.IsModal():
				self.EndModal(wx.ID_SAVE)
			else:
				self.Close()
		except ValueError as e:
			self._show_error_alert("Port should be a number")
		except InputError as e:
			self._show_error_alert(e.value)
	
	def _physical_input(self, event=None):
		if not self.machine_params:
			machine_name = self.machine_choice.GetStringSelection()
			machine = machine_registry.get(machine_name)
			info = machine.get_option_info()
			defaults = {k: v[0] for k, v in info.items()}
			self.machine_params = defaults
		try:
			self.machine.set_input_type(virtualmachine.MACHINE_INPUT_PHYSICAL, { 'machine_type' : self.machine_choice.GetStringSelection(), 'machine_options' : self.machine_params})
			if self.IsModal():
				self.EndModal(wx.ID_SAVE)
			else:
				self.Close()
		except TypeError as e:
			self._show_error_alert("Machine not configured")
		except InputError as e:
			self._show_error_alert(e.value)
	
	def _advanced_config(self, event=None):
		class Struct(object):
			def __init__(self, **kwargs):
				self.__dict__.update(kwargs)
		
		machine_name = self.machine_choice.GetStringSelection()
		machine = machine_registry.get(machine_name)
		info = machine.get_option_info()
		defaults = {k: v[0] for k, v in info.items()}
		self.machine_params = defaults
		
		config_instance = Struct(**defaults)
		dialog = None
		if 'port' in defaults:
			scd = SerialConfigDialog(config_instance, self, self.config)
			scd.ShowModal()  # SerialConfigDialog destroys itself.
		else:
			kbd = KeyboardConfigDialog(config_instance, self, self.config)
			kbd.ShowModal()
			kbd.Destroy()
		self.machine_params = config_instance.__dict__
		
	def _show_error_alert(self, message):
		alert_dialog = wx.MessageDialog(self, message, ERROR_DIALOG_TITLE, wx.OK | wx.ICON_ERROR)
		alert_dialog.ShowModal()
		alert_dialog.Destroy()


class OutputConfigurationDialog(wx.Dialog):
	"""A GUI for viewing and editing Plover configuration files.

	Changes to the configuration file are saved when the GUI is closed. Changes
	will take effect the next time the configuration file is read by the
	application, which is typically after an application restart.

	"""

	CONFIGURATION_TITLE = "Virtual Stenotype Output Configuration"

	other_instances = []
	
	def __init__(self, machine, config, parent):
		"""Create a configuration GUI based on the given config file.

		Arguments:

		configuration file to view and edit.
		during_plover_init -- If this is set to True, the configuration dialog
		won't tell the user that Plover needs to be restarted.
		"""

		pos = (400, 400)
		size = wx.Size(400, 200)
		wx.Dialog.__init__(self, parent, title=self.CONFIGURATION_TITLE, pos=pos, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.machine = machine
		self.parent = parent
		self.config = config

		# Close all other instances.
		if self.other_instances:
			for instance in self.other_instances:
				instance.Close()
		del self.other_instances[:]
		self.other_instances.append(self)

		sizer = wx.BoxSizer(wx.VERTICAL)

		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(wx.StaticText(self, label="Output type: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
		
		output_types = self.machine.get_output_types()
		
		self.output_type_choice = wx.Choice(self, choices=output_types)
		self.Bind(wx.EVT_CHOICE, self._update, self.output_type_choice)
		box.Add(self.output_type_choice, proportion=1, flag=wx.EXPAND)
		
		sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
		
		
		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		sizer.Layout()
		self._update()

		self.SetRect(AdjustRectToScreen(self.GetRect()))

		self.Bind(wx.EVT_CLOSE, self.on_close)
		
	def _update(self, event=None):
		# Refreshes the UI to reflect current data.
		output_type = self.machine.get_output_type()
		if (event or not output_type) and self.output_type_choice.GetStringSelection():
			output_type = self.output_type_choice.GetStringSelection()
		sizer = self.GetSizer()
		
		if len(sizer.GetChildren()) > 1:
			sizer.DeleteWindows()
			
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="Output type: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			output_types = self.machine.get_output_types()
			self.output_type_choice = wx.Choice(self, choices=output_types)
			self.Bind(wx.EVT_CHOICE, self._update, self.output_type_choice)
			box.Add(self.output_type_choice, proportion=1, flag=wx.EXPAND)			
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
		
		if output_type == virtualmachine.MACHINE_OUTPUT_SERIAL:
			self.output_type_choice.SetStringSelection(output_type)
			if machineserial.virtual_serial_ports_available():
				box = wx.BoxSizer(wx.HORIZONTAL)
				serial_config_button = wx.Button(self, label=SERIAL_CONFIG_BUTTON_NAME)
				self.Bind(wx.EVT_BUTTON, self._virtual_serial_config, serial_config_button)
				box.Add(serial_config_button)
				sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			box = wx.BoxSizer(wx.HORIZONTAL)
			machines = self.machine.get_serial_output_types()
			self.machine_choice = wx.Choice(self, choices=machines)
			if 'machine_type' in self.machine.get_output_params():
				self.machine_choice.SetStringSelection(self.machine.get_output_params()['machine_type'])
			if 'machine_options' in self.machine.get_output_params():
				self.machine_params = self.machine.get_output_params()['machine_options']
			else:
				self.machine_params = None
			box.Add(self.machine_choice, proportion=1, flag=wx.EXPAND)			
			self.config_button = wx.Button(self, id=wx.ID_PREFERENCES, label=CONFIG_BUTTON_NAME)
			box.Add(self.config_button)
			self.Bind(wx.EVT_BUTTON, self._advanced_config, self.config_button)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME) 
			self.Bind(wx.EVT_BUTTON, self._serial_output, button)
			sizer.Add(button, flag=wx.ALIGN_RIGHT)
		elif output_type == virtualmachine.MACHINE_OUTPUT_NETWORK:
			self.output_type_choice.SetStringSelection(output_type)
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="HOST: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			self.host_textctrl = wx.TextCtrl(self)
			if 'host' in self.machine.get_output_params():
				self.host_textctrl.SetValue(self.machine.get_output_params()['host'])
			else:
				self.host_textctrl.SetValue(machinenetwork.DEFAULT_HOST)
			box.Add(self.host_textctrl)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			
			box = wx.BoxSizer(wx.HORIZONTAL)
			box.Add(wx.StaticText(self, label="PORT: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
			self.port_textctrl = wx.TextCtrl(self)
			if 'port' in self.machine.get_output_params():
				self.port_textctrl.SetValue(str(self.machine.get_output_params()['port']))
			else:
				self.port_textctrl.SetValue(str(machinenetwork.DEFAULT_PORT))
			box.Add(self.port_textctrl)
			sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
			
			button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME)
			self.Bind(wx.EVT_BUTTON, self._network_output, button)
			sizer.Add(button, flag=wx.ALIGN_RIGHT)
		sizer.Layout()
		
	def _serial_output(self, event=None):
		if not self.machine_params:
			machine_name = self.machine_choice.GetStringSelection()
			machine = machine_registry.get(machine_name)
			info = machine.get_option_info()
			defaults = {k: v[0] for k, v in info.items()}
			self.machine_params = defaults
		try:
			self.machine.set_output_type(virtualmachine.MACHINE_OUTPUT_SERIAL, { 'machine_type' : self.machine_choice.GetStringSelection(), 'machine_options' : self.machine_params})
			if self.IsModal():
				self.EndModal(wx.ID_SAVE)
			else:
				self.Close()
		except Exception, e:
			self._show_error_alert(e)
			
	def _network_output(self, event=None):
		try:
			self.machine.set_output_type(virtualmachine.MACHINE_OUTPUT_NETWORK, { 'host' : self.host_textctrl.GetValue(), 'port' : int(self.port_textctrl.GetValue())})
			if self.IsModal():
				self.EndModal(wx.ID_SAVE)
			else:
				self.Close()
		except ValueError as e:
			self._show_error_alert("Port should be a number")
		except InputError as e:
			self._show_error_alert(e.value)
	
	def _advanced_config(self, event=None):
		class Struct(object):
			def __init__(self, **kwargs):
				self.__dict__.update(kwargs)
		
		machine_name = self.machine_choice.GetStringSelection()
		machine = machine_registry.get(machine_name)
		info = machine.get_option_info()
		defaults = {k: v[0] for k, v in info.items()}
		self.machine_params = defaults
		
		config_instance = Struct(**defaults)
		dialog = None
		if 'port' in defaults:
			scd = SerialConfigDialog(config_instance, self, self.config)
			scd.ShowModal()  # SerialConfigDialog destroys itself.
		else:
			kbd = KeyboardConfigDialog(config_instance, self, self.config)
			kbd.ShowModal()
		self.machine_params = config_instance.__dict__

	def _virtual_serial_config(self, event=None):
		vscd = VirtualSerialConfigDialog(self)
		vscd.ShowModal()

	def on_close(self, event):
		self.other_instances.remove(self)
		self.parent._update()
		event.Skip()
		
	def _show_error_alert(self, message):
		alert_dialog = wx.MessageDialog(self, message, ERROR_DIALOG_TITLE, wx.OK | wx.ICON_ERROR)
		alert_dialog.ShowModal()
		alert_dialog.Destroy()

	def _show_alert(self, message):
		alert_dialog = wx.MessageDialog(self, message, ALERT_DIALOG_TITLE, wx.OK)
		alert_dialog.ShowModal()
		alert_dialog.Destroy()

class VirtualSerialConfigDialog(wx.Dialog):

	CONFIGURATION_TITLE = 'Virtual Serial Configuration'
	CREATE_BUTTON_NAME = 'Create'

	def __init__(self, parent):

		self.parent = parent

		pos = (400, 400)
		wx.Dialog.__init__(self, parent, title=self.CONFIGURATION_TITLE, pos=pos, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

		ports = machineserial.get_default_ports()

		sizer = wx.BoxSizer(wx.VERTICAL)

		box = wx.BoxSizer(wx.HORIZONTAL)

		box.Add(wx.StaticText(self, label="Port 1: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
		self.port1_textctrl = wx.TextCtrl(self)
		if len(ports) > 0 and ports[0]:
			self.port1_textctrl.SetValue(str(ports[0]))
		box.Add(self.port1_textctrl)
		sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
		
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(wx.StaticText(self, label="Port 2: "), border=3, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
		self.port2_textctrl = wx.TextCtrl(self)
		if len(ports) > 0 and ports[1]:
			self.port2_textctrl.SetValue(str(ports[1]))
		box.Add(self.port2_textctrl)
		sizer.Add(box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)		
		
		button = wx.Button(self, label=self.CREATE_BUTTON_NAME) 
		self.Bind(wx.EVT_BUTTON, self._create_virtual_serial_ports, button)
		sizer.Add(button, flag=wx.ALIGN_RIGHT)

		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		sizer.Layout()

		self.SetRect(AdjustRectToScreen(self.GetRect()))

	def _create_virtual_serial_ports(self, event=None):
		if self.port1_textctrl.GetValue() and self.port2_textctrl.GetValue():
			try:
				machineserial.create_serial_port(self.port1_textctrl.GetValue(), self.port2_textctrl.GetValue())
				self.parent._show_alert("Virtual serial ports created")
			except Exception as e:
				self.parent._show_error_alert(e.value)