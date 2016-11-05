import wx
import re
import os
from wx.lib.utils import AdjustRectToScreen
import plover.gui.util as util
import plover.oslayer.outputcontrol as outputcontrol
import plover.config as conf
from wx.grid import EVT_GRID_LABEL_LEFT_CLICK, EVT_GRID_SELECT_CELL, EVT_GRID_RANGE_SELECT
from wx.grid import PyGridTableBase
from plover.gui.windows_handles_store import HandleEditorStore
from plover.gui.windows_handles_store import COLUMNS
from plover.gui.windows_handles_store import COL_WINDOW
from plover.gui.windows_handles_store import COL_HANDLE

TITLE = 'Plover: Windows Handles Editor'

FILTER_BY_WINDOW_TEXT = 'Filter by window:'
FILTER_BY_HANDLE_TEXT = 'Filter by handle:'
DO_FILTER_BUTTON_NAME = 'Filter'
INSERT_BUTTON_NAME = 'New'
EDIT_BUTTON_NAME = 'Edit Selected'
DELETE_BUTTON_NAME = 'Delete Selected'
SAVE_BUTTON_NAME = 'Save and Close'
CANCEL_BUTTON_NAME = 'Close'
ERROR_DIALOG_TITLE = 'Error'

REFRESH_IMAGE_FILE = os.path.join(conf.ASSETS_DIR, 'refresh.png')

NUM_COLS = len(COLUMNS)

class HandleEditor(wx.Dialog):

    BORDER = 3

    def __init__(self, parent, config, on_exit):
        pos = (config.get_dictionary_editor_frame_x(),
               config.get_dictionary_editor_frame_y())
        wx.Dialog.__init__(self, parent, title=TITLE, pos=pos,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.config = config
        self.on_exit = on_exit

        self.handle_filename = config.get_windows_handles_filename()

        # layout
        global_sizer = wx.BoxSizer(wx.VERTICAL)

        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)

        filter_left_sizer = wx.FlexGridSizer(2, 2, 4, 10)

        label = wx.StaticText(self, label=FILTER_BY_WINDOW_TEXT)
        filter_left_sizer.Add(label,
                              flag=wx.ALIGN_CENTER_VERTICAL,
                              border=self.BORDER)

        self.filter_by_window = wx.TextCtrl(self,
                                            style=wx.TE_PROCESS_ENTER,
                                            size=wx.Size(200, 20))
        self.Bind(wx.EVT_TEXT_ENTER, self._do_filter, self.filter_by_window)
        filter_left_sizer.Add(self.filter_by_window)

        label = wx.StaticText(self, label=FILTER_BY_HANDLE_TEXT)
        filter_left_sizer.Add(label,
                              flag=wx.ALIGN_CENTER_VERTICAL,
                              border=self.BORDER)

        self.filter_by_handle = wx.TextCtrl(self,
                                                 style=wx.TE_PROCESS_ENTER,
                                                 size=wx.Size(200, 20))
        self.Bind(wx.EVT_TEXT_ENTER,
                  self._do_filter,
                  self.filter_by_handle)
        filter_left_sizer.Add(self.filter_by_handle)

        filter_sizer.Add(filter_left_sizer, flag=wx.ALL, border=self.BORDER)

        do_filter_button = wx.Button(self, label=DO_FILTER_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._do_filter, do_filter_button)

        filter_sizer.Add(do_filter_button,
                         flag=wx.EXPAND | wx.ALL,
                         border=self.BORDER)

        global_sizer.Add(filter_sizer, flag=wx.ALL, border=self.BORDER)

        self.store = HandleEditorStore(config)

        # Grid
        self.grid = HandleEditorGrid(self, size=wx.Size(800, 600))
        self.grid.CreateGrid(self.store, 0, NUM_COLS)

        self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)

        self.grid.SetColSize(COL_WINDOW, 250)
        self.grid.SetColSize(COL_HANDLE, 250)

        global_sizer.Add(self.grid, 1, wx.EXPAND)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        insert_button = wx.Button(self, label=INSERT_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._insert_new, insert_button)

        buttons_sizer.Add(insert_button, flag=wx.ALL, border=self.BORDER)

        edit_button = wx.Button(self, label=EDIT_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._edit, edit_button)

        buttons_sizer.Add(edit_button, flag=wx.ALL, border=self.BORDER)

        delete_button = wx.Button(self, label=DELETE_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._delete, delete_button)

        buttons_sizer.Add(delete_button, flag=wx.ALL, border=self.BORDER)

        buttons_sizer.Add((0, 0), 1, wx.EXPAND)

        save_button = wx.Button(self, label=SAVE_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._save_close, save_button)

        buttons_sizer.Add(save_button, flag=wx.ALL, border=self.BORDER)

        cancel_button = wx.Button(self, label=CANCEL_BUTTON_NAME)
        self.Bind(wx.EVT_BUTTON, self._cancel_close, cancel_button)

        buttons_sizer.Add(cancel_button, flag=wx.ALL, border=self.BORDER)

        global_sizer.Add(buttons_sizer,
                         0,
                         flag=wx.EXPAND | wx.ALL,
                         border=self.BORDER)

        self.Bind(wx.EVT_MOVE, self._on_move)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self.SetAutoLayout(True)
        self.SetSizer(global_sizer)
        global_sizer.Fit(self)
        global_sizer.SetSizeHints(self)
        self.Layout()
        self.SetRect(AdjustRectToScreen(self.GetRect()))

        self.last_window = util.GetForegroundWindow()

    def _do_filter(self, event=None):
        self.store.ApplyFilter(self.filter_by_window.GetValue(),
                               self.filter_by_handle.GetValue())
        self.grid.RefreshView()

    def _insert_new(self, event=None):
        dlg = AddHandleConfigurationDialog(config=self.config, parent=self)
        dlg.Show()

    def _edit(self, event=None):
        self.grid.UpdateSelected()

    def _delete(self, event=None):
        delete_selection = [row for row in self.selection
                            if not self.store.is_row_read_only(row)]
        if delete_selection:

            # Delete in reverse order, so row numbers are stable.
            for row in sorted(delete_selection, reverse=True):
                self.store.DeleteSelected(row)
            self._table.ResetView(self)
        self.ClearSelection()

    def _save_close(self, event=None):
        self.store.SaveChanges()
        self.Close()

    def _cancel_close(self, event=None):
        self.Close()

    def _on_move(self, event):
        pos = self.GetScreenPositionTuple()
        self.config.set_dictionary_editor_frame_x(pos[0])
        self.config.set_dictionary_editor_frame_y(pos[1])
        event.Skip()

    def _on_close(self, event=None):
        result = wx.ID_YES
        if self.store.pending_changes:
            dlg = wx.MessageDialog(self,
                                   "You will lose your changes. Are you sure?",
                                   "Cancel",
                                   wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
        if result == wx.ID_YES:
            try:
                util.SetForegroundWindow(self.last_window)
            except:
                pass
            self.on_exit()
            self.Destroy()

class HandleEditorGrid(wx.grid.Grid):
    """ Dictionary Manager's grid """
    GRID_LABEL_WINDOW = "Window"
    GRID_LABEL_HANDLE = "Handle"
    sorted_labels = sorted([[COL_WINDOW, GRID_LABEL_WINDOW],
                            [COL_HANDLE, GRID_LABEL_HANDLE]])
    grid_labels = [pair[1] for pair in sorted_labels]

    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)

        self.parent = args[0]

        self._changedRow = None

        # We need to keep track of the selection ourselves...
        self.Bind(EVT_GRID_SELECT_CELL, self._on_select_cell)
        self.selection = set()

    def CreateGrid(self, store, rows, cols):
        """ Create the grid """

        wx.grid.Grid.CreateGrid(self, rows, cols)
        wx.grid.Grid.DisableDragRowSize(self)
        # TODO: enable this when wx is fixed...
        # self.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)

        self.store = store

        # Set GridTable
        self._table = HandleEditorGridTable(self.store)
        self.SetTable(self._table)

        self._sortingColumn = 0
        self._sortingAsc = None

        self.Bind(EVT_GRID_LABEL_LEFT_CLICK, self._onLabelClick)

    def RefreshView(self):
        self._table.ResetView(self)

    def InsertNew(self):
        for row in self.selection:
            if not self.store.is_row_read_only(row):
                self.store.InsertNew(row)
                self._table.ResetView(self)
                self.SetFocus()
                self.ClearSelection()
                self.SelectRow(row)
                self.SetGridCursor(row, 0)
                self.MakeCellVisible(row, 0)
                break
        else:
            self.ClearSelection()

    def UpdateSelected(self):
        if self.selection:

        updatee_selection = [row for row in self.selection
                            if not self.store.is_row_read_only(row)]
        if delete_selection:
            # Delete in reverse order, so row numbers are stable.
            for row in sorted(delete_selection, reverse=True):
                self.store.DeleteSelected(row)
            self._table.Reset

    def DeleteSelected(self):
        if self.selection:
            self.store.DeleteSelected(self.selection)
        self._table.ResetView(self)
        self.ClearSelection()

    def _onLabelClick(self, evt):
        """ Handle Grid label click"""

        if evt.Row == -1:
            if evt.Col >= 0:
                self.store.Sort(evt.Col)
                sort_column = self.store.GetSortColumn()
                sort_mode = self.store.GetSortMode()
                self._updateGridLabel(sort_column, sort_mode)
                self._table.ResetView(self)

        if evt.Col == -1:
            if evt.Row >= 0:
                self.SelectRow(evt.Row)
                self.SetGridCursor(evt.Row, 0)

    def _updateGridLabel(self, column, mode):
        """ Change grid's column labels """

        directionLabel = ""
        if mode is not None:
            directionLabel = " (asc)" if mode else " (desc)"
        for i in range(len(self.grid_labels)):
            label = (self.grid_labels[i] +
                     (directionLabel if column == i else ""))
            self._table.SetColLabelValue(i, label)

    def _on_select_cell(self, evt):
        row = evt.GetRow()
        self.selection = row

class HandleEditorGridTable(PyGridTableBase):
    """
    A custom wx.Grid Table using user supplied data
    """
    def __init__(self, store):
        """ Init GridTableBase with a Store. """

        # The base class must be initialized *first*
        PyGridTableBase.__init__(self)
        self.store = store
        cols = sorted([[COL_WINDOW, "Window"],
                       [COL_HANDLE, "Handle"]])
        self.col_names = [pair[1] for pair in cols]

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberCols(self):
        return len(self.col_names)

    def GetNumberRows(self):
        return self.store.GetNumberOfRows()

    def GetColLabelValue(self, col):
        return self.col_names[col]

    def SetColLabelValue(self, col, name):
        self.col_names[col] = name

    def GetRowLabelValue(self, row):
        return str(row + 1)

    def GetValue(self, row, col):
        return self.store.GetValue(row, col)

    def SetValue(self, row, col, value):
        self.store.SetValue(row, col, value)

    def GetAttr(self, row, col, params):
        if self.store.is_row_read_only(row):
            attr = wx.grid.GridCellAttr()
            attr.SetReadOnly(True)
            return attr
        return None

    def ResetView(self, grid):

        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(),
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(),
                wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,
                wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED)
        ]:
            if new < current:
                msg = wx.grid.GridTableMessage(self,
                                               delmsg,
                                               new,
                                               current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self,
                                               addmsg,
                                               new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = (wx.grid
               .GridTableMessage(self,
                                 wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES))
        grid.ProcessTableMessage(msg)

class AddHandleConfigurationDialog(wx.Dialog):
    """A GUI for viewing and editing Plover configuration files.

    Changes to the configuration file are saved when the GUI is closed. Changes
    will take effect the next time the configuration file is read by the
    application, which is typically after an application restart.

    """

    UI_BORDER = 4
    COMPONENT_SPACE = 3
    CONFIGURATION_TITLE = "Add window handle"
    WINDOW_TEXT = "Window:"
    HANDLE_TEXT = "Handle:"
    SEND_TEST_STRING_TEXT = "Send 'test' text"
    ADD_CONFIG_BUTTON_NAME = "Add"

    other_instances = []
    
    def __init__(self, config, parent, item=None):
        """Create a configuration GUI based on the given config file.

        Arguments:

        configuration file to view and edit.
        during_plover_init -- If this is set to True, the configuration dialog
        won't tell the user that Plover needs to be restarted.
        """

        pos = (config.get_config_frame_x(), config.get_config_frame_y())
        size = wx.Size(config.get_config_frame_width(), 
                       config.get_config_frame_height())
        wx.Dialog.__init__(self, parent, title=self.CONFIGURATION_TITLE, pos=pos, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.config = config
        self.parent = parent
        self.item = item

        self.refresh_bitmap = wx.Bitmap(REFRESH_IMAGE_FILE, wx.BITMAP_TYPE_PNG)

        # Close all other instances.
        if self.other_instances:
            for instance in self.other_instances:
                instance.Close()
        del self.other_instances[:]
        
        self.other_instances.append(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.windows = outputcontrol.get_open_windows()
        del self.windows['Focus window']

        self.window_name_box = wx.BoxSizer(wx.HORIZONTAL)
        self.window_name_box.Add(wx.StaticText(self, label=self.WINDOW_TEXT), border=self.COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        self.window_combo = wx.ComboBox(self, choices=self.windows.keys(), style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        if self.item:
            self.window_combo.SetValue(self.item['window'])

        self.window_name_box.Add(self.window_combo, proportion=1, flag=wx.EXPAND)
        
        self.Bind(wx.EVT_COMBOBOX, self._update, self.window_combo)
        self.Bind(wx.EVT_TEXT_ENTER, self._update, self.window_combo)

        self.refresh_button = wx.BitmapButton(self, bitmap=self.refresh_bitmap)
        self.refresh_button.Bind(wx.EVT_BUTTON, lambda e: wx.CallAfter(self._refresh_windows))
        self.window_name_box.Add(self.refresh_button, border=self.UI_BORDER)

        sizer.Add(self.window_name_box, border=self.UI_BORDER, flag=wx.ALL | wx.EXPAND)
        
        self.prev_window_choice = self.window_combo.GetValue()

        self.window_handle_box = wx.BoxSizer(wx.HORIZONTAL)
        self.window_handle_box.Add(wx.StaticText(self, label=self.HANDLE_TEXT), border=self.COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        self.handle_combo = wx.ComboBox(self, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        if item:
            self.handle_combo.SetValue(self.item['handle'])
        self.Bind(wx.EVT_COMBOBOX, self._update, self.handle_combo)
        self.window_handle_box.Add(self.handle_combo, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.window_handle_box, border=self.UI_BORDER, flag=wx.ALL | wx.EXPAND)

        self.test_button = wx.Button(self, label=self.SEND_TEST_STRING_TEXT)
        self.test_button.Enable(self._buttons_enabled())
        sizer.Add(self.test_button, flag=wx.ALL | wx.ALIGN_RIGHT, border=self.UI_BORDER)        

        # The bottom button container
        button_sizer = wx.StdDialogButtonSizer()

        # Configuring and adding the save button
        self.save_button = wx.Button(self, wx.ID_SAVE, self.ADD_CONFIG_BUTTON_NAME)
        self.save_button.SetDefault()
        self.save_button.Enable(self._buttons_enabled())
        button_sizer.AddButton(self.save_button)

        # Configuring and adding the cancel button
        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)
        button_sizer.Realize()

        sizer.Add(button_sizer, flag=wx.ALL | wx.ALIGN_RIGHT, border=self.UI_BORDER)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Layout()

        self.SetRect(AdjustRectToScreen(self.GetRect()))

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Bind(wx.EVT_BUTTON, self._save, self.save_button)

        self.Bind(wx.EVT_BUTTON, self.send_test_text, self.test_button)

    def on_close(self, event):
        self.other_instances.remove(self)
        #self.parent._update()
        event.Skip()    

    def _update(self, event=None):
        # Refreshes the UI to reflect current data.
        if event.GetEventObject() is self.window_combo:
            window_choice = self.window_combo.GetValue()
            if window_choice:
                if not outputcontrol.window_found(window_choice):
                    self._show_error_alert("Window not found")
                    return
                self.windows = outputcontrol.get_open_windows()
                windowname = window_choice
                if window_choice not in self.windows.keys():
                    pattern = re.compile(re.escape(window_choice), re.IGNORECASE)
                    for window in self.windows.keys():
                        if pattern.search(window):
                            windowname = window
                            break
                self.window_handles = outputcontrol.get_window_child_handles(self.windows[windowname]).keys()
                if len(self.window_handles) > 0:
                    self.window_handle_box.DeleteWindows()
                    self.window_handle_text = wx.StaticText(self, label=self.HANDLE_TEXT)
                    self.window_handle_box.Add(self.window_handle_text, border=self.COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
                    self.handle_combo = wx.ComboBox(self, choices=self.window_handles, style=wx.CB_DROPDOWN|wx.CB_READONLY)
                    self.Bind(wx.EVT_COMBOBOX, self._update, self.handle_combo)
                    self.window_handle_box.Add(self.handle_combo, proportion=1, flag=wx.EXPAND)
                    self.GetSizer().Layout()

        self.test_button.Enable(self._buttons_enabled())
        self.save_button.Enable(self._buttons_enabled())

    def _refresh_windows(self, event=None):
        # TODO: refresh open windows combo box
        self.windows = outputcontrol.get_open_windows()
        #del self.windows['Focus window']
        self.window_name_box.DeleteWindows()
        self.window_name_box.Add(wx.StaticText(self, label=self.WINDOW_TEXT), border=self.COMPONENT_SPACE, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        self.window_combo = wx.ComboBox(self, choices=self.windows.keys(), style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        self.window_name_box.Add(self.window_combo, proportion=1, flag=wx.EXPAND)
        self.window_name_box.Add(self.refresh_button, border=self.UI_BORDER)
        self.Bind(wx.EVT_COMBOBOX, self._update, self.window_combo)
        self.Bind(wx.EVT_TEXT_ENTER, self._update, self.window_combo)
        self.GetSizer().Layout()
    
    def _buttons_enabled(self):
        return not (not self.window_combo.GetValue() or not self.handle_combo.GetValue())

    def send_test_text(self, event=None):
        try:
            outputcontrol.send_test_text(windowname=self.window_combo.GetValue(), handlename=self.handle_combo.GetValue())
        except Exception, e:
            self._show_error_alert(e)

    def _save(self, event=None):
        # TODO: save new window:handle pair
        item = {'window':self.window_combo.GetValue(), 'handle':self.handle_combo.GetValue()}
        self.parent._update(item)
        self.Close()
        
    def _show_error_alert(self, message):
        alert_dialog = wx.MessageDialog(self, message, ERROR_DIALOG_TITLE, wx.OK | wx.ICON_ERROR)
        alert_dialog.ShowModal()
        alert_dialog.Destroy()

def Show(parent, config):
    if 'dialog_instance' not in Show.__dict__:
        Show.dialog_instance = None

    def clear_instance():
        Show.dialog_instance = None

    if Show.dialog_instance is None:
        Show.dialog_instance = HandleEditor(parent, config, clear_instance)
    Show.dialog_instance.Show()
    Show.dialog_instance.Raise()
    util.SetTopApp(Show.dialog_instance)
