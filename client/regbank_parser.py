from pdb import set_trace

sub_element_t   = namedtupple("sub_element_t", ["name", "width", "bit_position", "sw_attr", "hw_attr", "default_val", "description"]);
element_t       = namedtupple("element_t", ["offset_addr", "register_name", "sub_elements"]);
sheet_t         = namedtupple("sheet_t", ["sheet_name", "elements"]);
db_t            = namedtupple("db_t", "sheets");

def regbank_to_database(fname) :
    pass;

