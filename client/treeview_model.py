from pdb import set_trace
from PyQt4 import QtCore, QtGui


REGNAME_OR_SUBFIELD_COL         = 0     # Column 0 for register-name or subfield-name
REGADDR_OR_SUBFIELD_BITWIDTH    = 1     # Column 1 for register-address or subfield-bit specifications
REGVALUE_OR_SUBFIELD_VALUE      = 2     # Column 2 for register-value or subfield-bits value (in decimals, hex and binary representations)

BINARY_REPRESENTATION_THRESHOLD     = 3
DECIMAL_REPRESENTATION_THRESHOLD    = 32
HEX_REPRESENTATION_THRESHOLD        = 32

g_headers = ["Register/Subfield", "Base Address", "Value", "Default Value", "Description"]

class treeview_model_t (QtCore.QAbstractItemModel):
    def __init__(self, headers, parent=None):
        super(QtCore.QAbstractItemModel, self).__init__(parent)
        self.headers = headers
        self.regbanks = None

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        
        parent = index.internalPointer()

        if isinstance(parent, OrderedDict):
            return QtCore.QModelIndex()
        elif isinstance(parent, regbank_t):
            row = list(self.regbanks.keys()).index(parent._regbank_name)
            parent = self.regbanks
        elif isinstance(parent, module_instance_t):
            row = list(self.regbanks.keys()).index(parent._regbank_name)
            parent = self.regbanks[parent._regbank_name]
        elif isinstance(parent, register_t):
            row = dir(self.regbanks[parent._regbank_name]).index(parent._module_instance_name)
            parent = parent._module_instance
        elif isinstance(parent, subfield_t):
            row = dir(parent._register._module_instance).index(parent._register_name)
            parent = parent._register
        return self.createIndex(row, 0, parent)

    def flags(self, index):
            if not index.isValid():
                return 0
            if index.column()==2:
                return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        #print("data requested @ [{0}, {1}]".format(index.row(), index.column()))

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()
        if isinstance(item, OrderedDict):
            if index.column()==0:
                return list(item.keys())[index.row()]
        elif isinstance(item, regbank_t):
            if index.column()==0:
                return item._regbank_name
        elif isinstance(item, module_instance_t):
            if index.column()==0:
                return item._module_instance_name
            elif index.column()==1: 
                return hex(item._base_addr)
        elif isinstance(item, register_t):
            if index.column()==0:
                return item._register_name
            elif index.column()==1:
                return hex(item._get_addr())
            elif index.column()==2:
                return hex(item._stored_value)
            elif index.column()==3:
                return hex(item._default_val)
        elif isinstance(item, subfield_t):
            if index.column()==0:
                return item._subfield_name
            elif index.column()==2:
                return hex(item._stored_value)
            elif index.column()==3:
                return hex(item._default_val)
            elif index.column()==4:
                return item._description
            else:
                return None
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        
        if not parent.isValid():
            child = list(self.regbanks.values())[0]
        else:
            parent = parent.internalPointer()
            if isinstance(parent, OrderedDict):
                child = list(parent.values())[row]
            elif isinstance(parent, regbank_t):
                child = parent[row]
            elif isinstance(parent, module_instance_t):
                child = parent[row]
            elif isinstance(parent, register_t):
                child = parent[row]
        if child:
            return self.createIndex(row, column, child)
        else:
            return QtCore.QModelIndex()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False
        
        item = index.internalPointer()
        try:
            item._value = int(value, 0)
            self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
            return True
        except:
            return False

    def set_regbanks(self, regbanks):
        self.regbanks = regbanks

    def columnCount(self, parent):
        return len(self.headers)
    
    def headerData(self, section, orientation, role):
        if orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            return self.headers[section]
        else:
            return None

    def rowCount(self, parent):
        row_count = 0
        row = parent.row()
        column = parent.column()
        if not parent.isValid():
            row_count = len(self.regbanks)
        else:
            parent = parent.internalPointer()
            if isinstance(parent, subfield_t):
                row_count = 0
            else:
                row_count = len(parent)
        #print("rowCount = [{0}] for [{1}, {2}]".format(row_count, row, column))
        return row_count

class treeview_t(QtGui.QTreeView):
    def __init__(self, parent=None):
        super(QtGui.QTreeView, self).__init__(parent)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)

    def keyPressEvent(self, event):
        curr_index = self.currentIndex()
        if event.key()==QtCore.Qt.Key_Left:
            if self.isExpanded(curr_index):
                self.collapse(curr_index)
                return
            else:
                # Generate a new up-arrow key event and pass it
                event = QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Up, QtCore.Qt.NoModifier)
                QtGui.QTreeView.keyPressEvent(self, event)
                return
        elif event.key()==QtCore.Qt.Key_Right:
            if isinstance(curr_index.internalPointer(), subfield_t):
                # Generate a new down-arrow key event and pass it
                event = QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Down, QtCore.Qt.NoModifier)
                QtGui.QTreeView.keyPressEvent(self, event)
                return
            elif self.isExpanded(curr_index):
                event = QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Down, QtCore.Qt.NoModifier)
                QtGui.QTreeView.keyPressEvent(self, event)
                return
        elif event.key()==QtCore.Qt.Key_R:
            item = curr_index.internalPointer()
            if isinstance(item, register_t) or isinstance(item, subfield_t):
                # Update register with latest value
                pass
                return
        elif event.key()==QtCore.Qt.Key_W:
            item = curr_index.internalPointer()
            if isinstance(item, register_t) or isinstance(item, subfield_t):
                # Write register with current gui values
                pass
                return
        elif event.key()==QtCore.Qt.Key_E:
            item = curr_index.internalPointer()
            if isinstance(item, register_t) or isinstance(item, subfield_t):
                # Write register with current gui values
                pass
                index = self.model().index(curr_index.row(), 2, curr_index.parent())
                self.edit(index)
                return
        QtGui.QTreeView.keyPressEvent(self, event)

if __name__ == '__main__':
    import sys
    import argparse
    from regbank_parser import *
    QtCore.pyqtRemoveInputHook()
    app = QtGui.QApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', nargs=2, 
        help="Use specified excel sheet with regbank name")
    parser.add_argument('-u_id', nargs=1, help="Unique ID of target")
    parser.add_argument('-u_msg', nargs=1, help="Unique MSG of target")
    parse_res = parser.parse_args()
    f = parse_res.f
    u_id = parse_res.u_id
    u_msg = parse_res.u_msg
    demo = regbank_t(f[0], f[1])
    treemodel = treeview_model_t(g_headers, app)
    treemodel.set_regbanks(g_regbanks)
    view = treeview_t()
    view.setModel(treemodel)
    view.setWindowTitle("Simple Tree Model")
    view.setColumnWidth(0, 200)
    view.setColumnWidth(1, 100)
    view.setColumnWidth(2, 100)
    view.setColumnWidth(3, 100)
    view.setColumnWidth(4, 100)
    view.setColumnWidth(5, 200)
    view.show()
    view.setFixedSize(1000, 500)
    sys.exit(app.exec_())


