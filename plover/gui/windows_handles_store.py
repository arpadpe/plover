import plover.oslayer.win_window_handle_loader as handle_loader

WINDOW = 'WINDOW'
HANDLE = 'HANDLE'


# GUI will respect the order here:

COLUMNS = [WINDOW, HANDLE]

COL_WINDOW = COLUMNS.index(WINDOW)
COL_HANDLE = COLUMNS.index(HANDLE)


class HandleItem(object):

    def __init__(self, window, handle, id):

        if handle is None:
            handle = ''
        
        self.window = window
        self.handle = handle
        self.id = id


class HandleEditorStore(object):

    def __init__(self, config):

        self.config = config

        self.all_keys = []
        self.filtered_keys = []
        self.sorted_keys = []

        self.sorting_column = -1
        self.sorting_mode = None

        item_id = 0
        self.new_id = -1

        self.pending_changes = False

        self.handles_filename = config.get_windows_handles_filename()

        self.handles = handle_loader.load_window_handles(self.handles_filename)

        for window, handle in self.handles.iteritems():
            item = HandleItem(window,
                              handle,
                              item_id)
            self.all_keys.append(item)
            item_id += 1

        self.filtered_keys = self.all_keys[:]
        self.sorted_keys = self.filtered_keys[:]

    def is_row_read_only(self, row):
        # Make all rows read only
        return True

    def GetNumberOfRows(self):
        return len(self.sorted_keys)

    def GetValue(self, row, col):
        item = self.sorted_keys[row]
        result = ""

        if col is COL_WINDOW:
            result = item.window
        elif col is COL_HANDLE:
            result = item.handle
        return result

    def SetValue(self, row, col, value):
        self.pending_changes = True
        editing_item = self.sorted_keys[row]
        if col is COL_WINDOW:
            editing_item.window = value
        elif col is COL_HANDLE:
            editing_item.handle = value

    def GetSortColumn(self):
        return self.sorting_column

    def GetSortMode(self):
        return self.sorting_mode

    def ApplyFilter(self, window_filter, handle_filter):
        self.filtered_keys = []
        self.sorted_keys = []
        for item in self.all_keys:
            if self._itemMatchesFilter(item, window_filter, handle_filter):
                self.filtered_keys.append(item)
        self._applySort()

    def InsertNew(self, row, window, handle):
        self.pending_changes = True
        item = HandleItem(window, handle, self.new_id)
        self.all_keys.append(item)
        self.sorted_keys.insert(row, item)
        self.new_id -= 1

    def UpdateSelected(self, row, window, handle):
        self.pending_changes = True
        editing_item = self.sorted_keys[row]
        if editing_item.window != window:
            editing_item.window = window
        if editing_item.handle != handle:
            editing_item.handle = handle

    def DeleteSelected(self, row):
        self.pending_changes = True
        item = self.sorted_keys[row]
        self.sorted_keys.remove(item)

    def SaveChanges(self):
        if True:
        #if self.pending_changes:
            self.pending_changes = False

            handles = dict()
            for item in self.all_keys:
                handles[item.window] = item.handle

            handle_loader.save_window_handles(self.handles_filename, handles)

    def Sort(self, column):
        if column is not COL_WINDOW and column is not COL_HANDLE:
            return

        if self.sorting_column == column:
            # Already sorting on this column
            # Next sorting mode
            self.sorting_mode = self._cycleNextSortMode(self.sorting_mode)
        else:
            # Different column than the one currently being sorted
            self.sorting_column = column
            # First sorting mode
            self.sorting_mode = True
        self._applySort()

    def _getAddedItem(self, id):
        for item in self.added_items:
            if item.id == id:
                return item
        return None

    def _itemMatchesFilter(self, item, window_filter, handle_filter):
        window_add = False
        handle_add = False
        if window_filter:
            window = item.window
            if window:
                if window.lower().startswith(window_filter.lower()):
                    window_add = True
        else:
            window_add = True
        if handle_filter:
            handle = item.handle
            if handle:
                if handle.lower().startswith(handle_filter.lower()):
                    handle_add = True
        else:
            handle_add = True
        return window_add and handle_add

    def _cycleNextSortMode(self, sort_mode):
        if sort_mode is None:
            return True
        elif sort_mode is True:
            return False
        else:
            return None

    def _applySort(self):
        if self.sorting_mode is not None:
            reverse_sort = not self.sorting_mode
            if self.sorting_column is COL_WINDOW:
                self.sorted_keys = sorted(self.filtered_keys,
                                          key=lambda x: x.window.lower(),
                                          reverse=reverse_sort)
            elif self.sorting_column is COL_HANDLE:
                self.sorted_keys = sorted(self.filtered_keys,
                                          key=lambda x: x.handle.lower(),
                                          reverse=reverse_sort)
        else:
            self.sorted_keys = self.filtered_keys[:]
