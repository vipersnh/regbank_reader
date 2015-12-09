
REGNAME_OR_SUBFIELD_COL         = 0     # Column 0 for register-name or subfield-name
REGADDR_OR_SUBFIELD_BITWIDTH    = 1     # Column 1 for register-address or subfield-bit specifications
REGVALUE_OR_SUBFIELD_VALUE      = 2     # Column 2 for register-value or subfield-bits value (in decimals, hex and binary representations)

BINARY_REPRESENTATION_THRESHOLD     = 3
DECIMAL_REPRESENTATION_THRESHOLD    = 32
HEX_REPRESENTATION_THRESHOLD        = 32

g_headers = ["Sheet Name", "Regname / Subfield name", "Address", "Value", "Description"]

class data_item_t:
    def __init__(self, sheets):
        self.sheets = sheets

    def update_sheets

class treeview_model_t (QAbstractItemModel):
    def __init__(self, sheets, parent=None):
        super(QAbstractItemModel, self).__init__(parent)
        self.sheets = sheets


