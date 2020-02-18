
import wx
from wx.lib.utils import AdjustRectToScreen
import sys
import plover.gui.util as util
import plover.oslayer.outputcontrol as outputcontrol
import plover.gui.windows_handles_editor as handles_editor

UI_BORDER = 4
COMPONENT_SPACE = 3
TITLE = "Plover: Output flow"
TRANSLATE_FLOW_TEXT = "Translate flow"
REVERSE_DICTIONARY_ORDER_TEXT = "Reverse dictionary order"
SEND_BACKSPACES_TEXT = "Send backspaces"
OUTPUT_WINDOW_TEXT = "Output window:"
OUTPUT_WINDOW_HANDLE_TEXT = "Window handle:"
HANDLES_EDITOR_BUTTON_NAME = "Handles Settings"
ADD_CONFIG_BUTTON_NAME = "Add"
SAVE_CONFIG_BUTTON_NAME = "Save"
ERROR_DIALOG_TITLE = 'Error'

class OutputFlowDialog(wx.Dialog):
    """  """

    # Keep track of other instances of ConfigurationDialog.
    other_instances = []
    
    def __init__(self, config, parent, flow_control):
        """Create a configuration GUI based on the given config file.

        Arguments:

        configuration file to view and edit.
        during_plover_init -- If this is set to True, the configuration dialog
        won't tell the user that Plover needs to be restarted.
        """
        pos = (config.get_config_frame_x(), config.get_config_frame_y())
        size = wx.Size(config.get_config_frame_width(), 
                       config.get_config_frame_height())
        wx.Dialog.__init__(self, parent, title=TITLE, pos=pos, size=size, 
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.config = config
        self.parent = parent
        self.flow_control = flow_control
        self.index = flow_control['index']

        self.display_handle_config = outputcontrol.get_handle_needed()

        # Close all other instances.
        if self.other_instances:
            for instance in self.other_instances:
                instance.Close()
        del self.other_instances[:]
        self.other_instances.append(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.translate_flow = wx.CheckBox(self, label=TRANSLATE_FLOW_TEXT)
        self.translate_flow.SetValue(self.flow_control['translated'])
        sizer.Add(self.translate_flow, border=UI_BORDER, flag=wx.ALL)

        self.reverse_dictionary_order = wx.CheckBox(self, label=REVERSE_DICTIONARY_ORDER_TEXT)
        self.reverse_dictionary_order.SetValue(self.flow_control['dict_reversed'])
        sizer.Add(self.reverse_dictionary_order, border=UI_BORDER, flag=wx.ALL)

        self.send_backspaces = wx.CheckBox(self, label=SEND_BACKSPACES_TEXT)
        self.send_backspaces.SetValue(self.flow_control['send_backspaces'])
        sizer.Add(self.send_backspaces, border=UI_BORDER, flag=wx.ALL)

        self.windows = outputcontrol.get_open_windows();

        window_name_box = wx.BoxSizer(wx.HORIZONTAL)
        window_name_box.Add(wx.StaticText(self, label=OUTPUT_WINDOW_TEXT), border=COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        self.window_choice = wx.Choice(self, choices=self.windows.keys())
        if self.flow_control['window'] in self.windows:
            self.window_choice.SetStringSelection(self.flow_control['window'])
        window_name_box.Add(self.window_choice, proportion=1, flag=wx.EXPAND)
        self.Bind(wx.EVT_CHOICE, self._update, self.window_choice)
        sizer.Add(window_name_box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
        
        if self.display_handle_config:
            self.window_handle_box = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(self.window_handle_box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
        
            handles_editor_button = wx.Button(self, label=HANDLES_EDITOR_BUTTON_NAME)
            handles_editor_button.Bind(wx.EVT_BUTTON, self._show_handles_editor)

            sizer.Add(handles_editor_button, flag=wx.ALL | wx.ALIGN_RIGHT, border=UI_BORDER)

        # The bottom button container
        button_sizer = wx.StdDialogButtonSizer()

        # Configuring and adding the save button
        self.save_button = wx.Button(self, wx.ID_SAVE, ADD_CONFIG_BUTTON_NAME)
        self.save_button.SetDefault()
        self.save_button.Enable(self.save_button_enabled())
        button_sizer.AddButton(self.save_button)

        # Configuring and adding the cancel button
        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        sizer.Add(button_sizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=UI_BORDER)

        self.SetSizer(sizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetAutoLayout(True)
        self._update()
        sizer.Layout()
        
        # Binding the save button to the self._save callback
        self.Bind(wx.EVT_BUTTON, self._save, self.save_button)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _update(self, event=None):
        self.save_button.Enable(self.save_button_enabled())
        if not self.display_handle_config:
            return
        self.window_handle_box.DeleteWindows()
        windowname = self.window_choice.GetStringSelection()
        if windowname == 'Focus window':
            return
        if windowname:
            window_handle = outputcontrol.get_handle_for_window(self.config.get_windows_handles_filename(), windowname)
            if window_handle:
                window_handle_text = wx.StaticText(self, label=OUTPUT_WINDOW_HANDLE_TEXT)
                self.window_handle_box.Add(window_handle_text, border=COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
                window_handle_text = wx.StaticText(self, label=window_handle)
                self.window_handle_box.Add(window_handle_text, border=COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
            else:
                self._show_error_alert('''Window handle for ''' + windowname + ''' unknown
                                        \nEdit window handles in Handles Settings!''')

        self.GetSizer().Layout()
                
    def save_button_enabled(self):
        windowname = self.window_choice.GetStringSelection()
        if windowname and (windowname == 'Focus window' or not self.display_handle_config):
            return True
        if windowname:
            window_handle = outputcontrol.get_handle_for_window(self.config.get_windows_handles_filename(), windowname)
            if window_handle:
                return True
        return False

    def on_close(self, event):
        self.other_instances.remove(self)
        event.Skip()

    def _save(self, event=None):
        self.flow_control = {'window':self.window_choice.GetStringSelection(),
                            'enabled':True,
                            'translated':self.translate_flow.GetValue(),
                            'dict_reversed':self.reverse_dictionary_order.GetValue(),
                            'send_backspaces':self.send_backspaces.GetValue(),
                            'index':self.index}

        self.parent.update_row(self.flow_control)

        if self.IsModal():
            self.EndModal(wx.ID_SAVE)
        else:
            self.Close()

    def _show_handles_editor(self, event=None):
        handles_editor.Show(self, self.config)

    def _show_error_alert(self, message):
        alert_dialog = wx.MessageDialog(self, message, ERROR_DIALOG_TITLE, wx.OK | wx.ICON_ERROR)
        alert_dialog.ShowModal()
        alert_dialog.Destroy()

def Show(config, parent, flow_control):
    dialog_instance = OutputFlowDialog(config, parent, flow_control)
    dialog_instance.Show()
    dialog_instance.Raise()
    util.SetTopApp(dialog_instance)