
import wx
from wx.lib.utils import AdjustRectToScreen
import sys
import plover.gui.util as util
import plover.oslayer.outputcontrol as outputcontrol

UI_BORDER = 4
COMPONENT_SPACE = 3
TITLE = "Plover: Secondary flow"
TRANSLATE_FLOW_TEXT = "Translate flow"
REVERSE_DICTIONARY_ORDER_TEXT = "Reverse dictionary order"
OUTPUT_WINDOW_TEXT = "Output window:"
OUTPUT_WINDOW_HANDLE_TEXT = "Window handle:"
SAVE_CONFIG_BUTTON_NAME = "Add"
WINDOW_HANDLE_INFO = """Choose handle class for the window, 
                    \nMS Word - _WwG, Notepad - Edit, Notepad++ - Scintilla, Sublime Text 2 - PX_WINDOW_CLASS 
                    \nYou can find the handle class name of a window using WinSpy++"""

class SecondaryFlowDialog(wx.Dialog):
    """  """

    # Keep track of other instances of ConfigurationDialog.
    other_instances = []
    
    def __init__(self, config, parent, index):
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
        self.index = index

        print index

        # Close all other instances.
        if self.other_instances:
            for instance in self.other_instances:
                instance.Close()
        del self.other_instances[:]
        self.other_instances.append(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.translate_flow = wx.CheckBox(self, label=TRANSLATE_FLOW_TEXT)
        self.translate_flow.SetValue(config.get_output_translated(self.index))
        sizer.Add(self.translate_flow, border=UI_BORDER, flag=wx.ALL)

        self.reverse_dictionary_order = wx.CheckBox(self, label=REVERSE_DICTIONARY_ORDER_TEXT)
        self.reverse_dictionary_order.SetValue(config.get_output_dictionary_order_reversed(self.index))
        sizer.Add(self.reverse_dictionary_order, border=UI_BORDER, flag=wx.ALL)

        self.windows = outputcontrol.get_open_windows();

        window_name_box = wx.BoxSizer(wx.HORIZONTAL)
        window_name_box.Add(wx.StaticText(self, label=OUTPUT_WINDOW_TEXT), border=COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        self.window_choice = wx.Choice(self, choices=self.windows.keys())
        if self.config.get_output_window(self.index) in self.windows:
            self.window_choice.SetStringSelection(self.config.get_output_window(self.index))
        window_name_box.Add(self.window_choice, proportion=1, flag=wx.EXPAND)
        self.Bind(wx.EVT_CHOICE, self._update, self.window_choice)
        sizer.Add(window_name_box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
        
        self.window_handle_box = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.window_handle_box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)

        self.handle_info_box = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.handle_info_box, border=UI_BORDER, flag=wx.ALL | wx.EXPAND)
        
        # The bottom button container
        button_sizer = wx.StdDialogButtonSizer()

        # Configuring and adding the save button
        save_button = wx.Button(self, wx.ID_SAVE, SAVE_CONFIG_BUTTON_NAME)
        save_button.SetDefault()
        button_sizer.AddButton(save_button)

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
        self.Bind(wx.EVT_BUTTON, self._save, save_button)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _update(self, event=None):
        if self.window_choice.GetStringSelection():
            print self.windows
            self.window_handles = outputcontrol.get_window_child_handles(self.windows[self.window_choice.GetStringSelection()]).keys()
            if len(self.window_handles) > 0:
                self.window_handle_box.DeleteWindows()
                self.window_handle_text = wx.StaticText(self, label=OUTPUT_WINDOW_HANDLE_TEXT)
                self.window_handle_box.Add(self.window_handle_text, border=COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
                self.handle_choice = wx.Choice(self, choices=self.window_handles)
                self.handle_choice.SetStringSelection(self.config.get_output_windows_handle(self.index))
                self.window_handle_box.Add(self.handle_choice, proportion=1, flag=wx.EXPAND)
                self.handle_info_box.DeleteWindows()
                self.GetSizer().Layout()
                
    def on_close(self, event):
        self.other_instances.remove(self)
        event.Skip()

    def _save(self, event):
        self.config.set_output_translated(self.translate_flow.GetValue(), self.index)
        self.config.set_output_dictionary_order_reversed(self.reverse_dictionary_order.GetValue(), self.index)
        self.config.set_output_window(self.window_choice.GetStringSelection(), self.index)
        self.config.set_output_windows_handle(self.handle_choice.GetStringSelection(), self.index)

        self.parent.update_row( self.window_choice.GetStringSelection(), self.index)

        with open(self.config.target_file, 'wb') as f:
            self.config.save(f)

        if self.IsModal():
            self.EndModal(wx.ID_SAVE)
        else:
            self.Close()

def Show(config, parent, index):
    dialog_instance = SecondaryFlowDialog(config, parent, index)
    dialog_instance.Show()
    dialog_instance.Raise()
    util.SetTopApp(dialog_instance)