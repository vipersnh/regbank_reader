import xlrd
from os.path import basename, splitext
from pdb import set_trace
from collections import namedtuple

sub_element_t   = namedtuple("sub_element_t", ["name", "bit_width", "bit_position", "sw_attr", "hw_attr", "default_val", "description"]);
element_t       = namedtuple("element_t", ["offset_addr", "register_name", "sub_elements"]);
sheet_t         = namedtuple("sheet_t", ["sheet_name", "elements"]);
db_t            = namedtuple("db_t", ["regbank_name", "sheets"]);

## Columns information
regbank_info = {"start_row_idx"      :1,
                "offset_address_col" :0,
                "register_name_col"  :1,
                "sub_field_name_col" :2,
                "bit_width_col"      :3,
                "bit_position_col"   :4,
                "sw_attr_col"        :5,
                "hw_attr_col"        :6,
                "default_value_col"  :7,
                "description_col"    :8};


def regbank_decode_elements(rows) :
    element = element_t(offset_addr     = int(rows[0][regbank_info["offset_address_col"]].value),
                        register_name   = rows[0][regbank_info["register_name_col"]].value,
                        sub_elements    = []);
    sw_attr = rows[0][regbank_info["sw_attr_col"]].value;
    hw_attr = rows[0][regbank_info["hw_attr_col"]].value;
    for row in rows :
        sub_element = sub_element_t(
                name = row[regbank_info["sub_field_name_col"]].value,
                bit_width = int(row[regbank_info["bit_width_col"]].value),
                bit_position = row[regbank_info["bit_position_col"]].value,
                sw_attr = sw_attr,
                hw_attr = hw_attr,
                default_val = row[regbank_info["default_value_col"]].value,
                description = row[regbank_info["description_col"]].value);
        element.sub_elements.append(sub_element);
    if element.register_name=='':
        return None;
    else:
        return element;

def regbank_to_database(fname) :
    workbook = xlrd.open_workbook(fname);
    regbank_name = splitext(basename(fname))[0];
    db = db_t(regbank_name, sheets=[]);
    for i in range(0, workbook.nsheets) :
        xl_sheet = workbook.sheet_by_index(i);
        sheet = sheet_t(sheet_name=xl_sheet.name, elements=[]);
        row_idx = regbank_info["start_row_idx"];
        while 1:
            row_line = xl_sheet.row(row_idx);
            rows = [];
            rows.append(xl_sheet.row(row_idx));
            row_idx += 1;
            while (row_idx<xl_sheet.nrows) and (xl_sheet.row(row_idx)[regbank_info["offset_address_col"]].value==''):
                rows.append(xl_sheet.row(row_idx));
                row_idx += 1;
            element = regbank_decode_elements(rows);
            if element!=None:
                sheet.elements.append(element);
            if row_idx>=xl_sheet.nrows :
                break;
        db.sheets.append(sheet);
    return db;

def regbank_offset_size_predict(db):
    return None;


