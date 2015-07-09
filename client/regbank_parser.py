import xlrd
from os.path import basename, splitext
from pdb import set_trace
from collections import namedtuple
from StructDict import StructDict
import enumeration

class offsets_enum_t(enumeration.Enum):
    BYTE_OFFSETS = 0
    WORD_OFFSETS = 1


subfield_t      = StructDict("subfield_t", ["bit_width", "bit_position", "sw_attr", 
                             "hw_attr", "default_val", "description"])
register_t      = StructDict("register_t", ["offset_addr", "subfields"])
sheet_t         = StructDict("sheet_t", ["base_addr", "registers"])
## Register Access from  db
#  db["regbank"]["sheet"]["register"] = 
db              = dict()

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



regbank_files = dict()  # Dict of all regbank files to be opened for reading, keyed by regbank_name

def regbank_decode_register(rows) :
    register_name = rows[0][regbank_info["register_name_col"]].value
    register = register_t()
    register.offset_addr =int(rows[0][regbank_info["offset_address_col"]].value)
    register.subfields = dict()
    sw_attr = rows[0][regbank_info["sw_attr_col"]].value
    hw_attr = rows[0][regbank_info["hw_attr_col"]].value
    for row in rows :
        subfield    = subfield_t()
        subfield_name = row[regbank_info["sub_field_name_col"]].value
        subfield.bit_width = int(row[regbank_info["bit_width_col"]].value)
        subfield.bit_position = row[regbank_info["bit_position_col"]].value
        subfield.sw_attr = sw_attr
        subfield.hw_attr = hw_attr
        subfield.default_val = row[regbank_info["default_value_col"]].value
        subfield.description = description = row[regbank_info["description_col"]].value
        assert subfield_name not in register.subfields.keys(), "Subfield name already present"
        register.subfields[subfield_name] = subfield
    if element.register_name=='':
        assert 0, "Handle this condition"
    else:
        return [register_name, register];

def regbank_to_load(fname) :
    regbank_name = splitext(basename(fname))[0]
    regbank_files[regbank_name] = fname
    db[regbank_name] = dict()

def regbank_get_sheetnames(fname):
    # TODO for GUI
    pass

def regbank_load_sheet(regbank_name, sheet_name, base_addr, offset_type=None, as_sheet_name=None):
    assert regbank_name in regbank_files.keys(), "Regbank file must be loaded before loading sheets"
    workbook = xlrd.open_workbook(regbank_files[regbank_name])
    assert sheet_name in workbook.sheet_names(), "Loaded regbank doesnt contain sheet specified"
    xl_sheet = workbook.sheet_by_name(sheet_name)
    row_idx = regbank_info["start_row_idx"]
    db[regbank_name][sheet_name] = sheet_t()
    while 1:
        row_line = xl_sheet.row(row_idx)
        rows = []
        rows.append(xl_sheet.row(row_idx))
        row_idx += 1
        while (row_idx<xl_sheet.nrows) and (xl_sheet.row(row_idx)[regbank_info["offset_address_col"]].value==''):
            rows.append(xl_sheet.row(row_idx))
            row_idx += 1
        [register_name, register] = regbank_decode_register(rows)
        db[regbank_name][sheet_name][register_name] = register
        if row_idx>=xl_sheet.nrows :
            break
    set_trace()
    pass
#    workbook = xlrd.open_workbook(fname)
#    regbank = splitext(basename(fname))[0]
#    db = {}
#    for i in range(0, workbook.nsheets) :
#        xl_sheet = workbook.sheet_by_index(i)
#        sheet = sheet_t()
#        row_idx = regbank_info["start_row_idx"]
#        while 1:
#            row_line = xl_sheet.row(row_idx)
#            rows = []
#            rows.append(xl_sheet.row(row_idx))
#            row_idx += 1
#            while (row_idx<xl_sheet.nrows) and (xl_sheet.row(row_idx)[regbank_info["offset_address_col"]].value==''):
#                rows.append(xl_sheet.row(row_idx))
#                row_idx += 1
#            element = regbank_decode_elements(rows)
#            if element!=None:
#                sheet.elements.append(element)
#            if row_idx>=xl_sheet.nrows :
#                break
#        db.sheets.append(sheet)
#    return db

def regbank_offset_size_predict(db):
    assert 0, "Handle this"
    return None;

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs="+")
    parse_res = parser.parse_args()
    fnames = parse_res.fnames
    regbank_to_load(fnames[0])
    regbank_load_sheet("demo_regbank", "Sheet_A", offsets_enum_t.WORD_OFFSETS, 0x4000000)


