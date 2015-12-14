
REGNAME_OR_SUBFIELD_COL         = 0     # Column 0 for register-name or subfield-name
REGADDR_OR_SUBFIELD_BITWIDTH    = 1     # Column 1 for register-address or subfield-bit specifications
REGVALUE_OR_SUBFIELD_VALUE      = 2     # Column 2 for register-value or subfield-bits value (in decimals, hex and binary representations)

BINARY_REPRESENTATION_THRESHOLD     = 3
DECIMAL_REPRESENTATION_THRESHOLD    = 32
HEX_REPRESENTATION_THRESHOLD        = 32

g_headers = ["Sheet Name", "Regname / Subfield name", "Address", "Value", "Description"]

class data_item_t:
    def __init__(self, sheet_name, register_name=None, subfield_name=None, value=None):
        self.is_sheet = register_name == None
        self.is_register = subfield_name == None and sheet_name != None
        self.is_subfield = subfield_name != None and register_name != None
        self.sheet_name = sheet_name
        self.register_name = register_name
        self.subfield_name = subfield_name
        self.value = value

    def get_updated_value(self):
        # Update value from server
    
    def set_updated_value(self, value):
        # Update the server with the value

class treenode_t :
    def __init__(self, parent, item):
        self.parent = parent
        self.item   = item
        self.children = list()
        self.row = 0

    def append_child(self, child):
        self.rows += 1
        self.children.append(child)

    def get_child(self, idx):
        assert idx < len(self.children)
        return self.children[idx]

class treeview_model_t (QAbstractItemModel):
    def __init__(self, sheets, parent=None):
        super(QAbstractItemModel, self).__init__(parent)
        self.sheets = sheets


