import xlrd
import re
from os.path import basename, splitext
from pdb import set_trace
from collections import namedtuple, OrderedDict
from StructDict import StructDict
import enumeration

class offsets_enum_t(enumeration.Enum):
    BYTE_OFFSETS = 0
    WORD_OFFSETS = 1


subfield_t      = StructDict("subfield_t", ["name", "bit_width", "bit_position", "sw_attr", 
                                            "hw_attr", "default_val", "description", "value"])
register_t      = StructDict("register_t", ["offset_addr", "subfields", "value"])
sheet_t         = StructDict("sheet_t",    ["base_addr","mmap_done", "start_addr", "end_addr", "offset_type", "registers"])
## Register Access from  db
#  db["regbank"]["sheet"]["register"] = 
db              = OrderedDict()
db_dict         = dict()


## Columns information
regbank_info = {"start_row_header"   :"Offset address",
                "offset_address_col" :0,
                "register_name_col"  :1,
                "sub_field_name_col" :2,
                "bit_width_col"      :3,
                "bit_position_col"   :4,
                "sw_attr_col"        :5,
                "hw_attr_col"        :6,
                "default_value_col"  :7,
                "description_col"    :8,
                "reserved_keyword"   :"RESERVED"};



regbank_files = OrderedDict()  # Dict of all regbank files to be opened for reading, 
                        # keyed by regbank_name

def regbank_decode_register(rows) :
    register_name = rows[0][regbank_info["register_name_col"]].value
    register = register_t()
    register.offset_addr =int(rows[0][regbank_info["offset_address_col"]].value)
    register.subfields = OrderedDict()
    sw_attr = rows[0][regbank_info["sw_attr_col"]].value
    hw_attr = rows[0][regbank_info["hw_attr_col"]].value
    reserved_idx = 0
    for row in rows :
        subfield    = subfield_t()
        subfield_name = row[regbank_info["sub_field_name_col"]].value
        subfield.name = subfield_name
        subfield.bit_width = int(row[regbank_info["bit_width_col"]].value)
        subfield.bit_position = row[regbank_info["bit_position_col"]].value
        assert 'x' not in subfield.bit_position, "Invalid x in bit_position field"
        if ':' in subfield.bit_position:
            [end, start] = re.findall("\d+", subfield.bit_position)
        else:
            [start] = re.findall("\d+", subfield.bit_position)
            end = start
        start = int(start); end = int(end)
        subfield.bit_position = list(range(start, end+1))
        subfield.sw_attr = sw_attr
        subfield.hw_attr = hw_attr
        subfield.default_val = int(row[regbank_info["default_value_col"]].value)
        subfield.description = description = row[regbank_info["description_col"]].value
        if re.search(regbank_info["reserved_keyword"], subfield_name, re.IGNORECASE):
            subfield_name = regbank_info["reserved_keyword"] + str(reserved_idx)
            reserved_idx += 1
        try:
            assert subfield_name not in register.subfields.keys(), \
                "Subfield name already present"
        except:
            set_trace()
            pass
        register.subfields[subfield_name] = subfield
    if register_name=='':
        return [None, None]
    else:
        return [register_name, register];

def regbank_get_subfield_value(subfield, value):
    bit_pos = subfield.bit_position
    start = bit_pos[0]
    end   = bit_pos[-1]
    mask  = ((1<<(end+1))-1) - ((1<<(start))-1)
    try:
        return ( value & mask ) >> start
    except:
        set_trace()
        pass

def regbank_load_excel(fname) :
    regbank_name = splitext(basename(fname))[0]
    regbank_files[regbank_name] = fname
    db[regbank_name] = OrderedDict()
    for sheet_name in xlrd.open_workbook(fname).sheet_names():
        db[regbank_name][sheet_name] = None
        regbank_make_struct(regbank_name, sheet_name)

def regbank_unload(regbank_name):
    if regbank_name in db.keys():
        db.pop(regbank_name)

def regbank_load_excel_all_sheets(fname) :
    # TODO for GUI
    pass

def regbank_get_sheetnames(fname):
    # TODO for GUI
    pass

def regbank_make_struct(regbank_name, sheet_name):
    try:
        regbank = db_dict[regbank_name]
    except:
        regbank = StructDict("regbank")
        setattr(regbank, "__regbank_name__", regbank_name)
    sheet = StructDict("regbank_sheet")
    setattr(sheet, "__sheet_name__", sheet_name)
    setattr(sheet, "__regbank_name__", regbank_name)
    if db[regbank_name][sheet_name]:
        for (register_name, cur_register) in db[regbank_name][sheet_name].registers.items():
            register = StructDict("regbank_register") 

            setattr(register, "__register_name__", register_name)
            setattr(register, "__sheet_name__", sheet_name)
            setattr(register, "__regbank_name__", regbank_name)
            for (subfield_name, cur_subfield) in cur_register.subfields.items():
                subfield = StructDict("regbank_subfield")
                setattr(subfield, "__subfield_name__", subfield_name)
                setattr(subfield, "__register_name__", register_name)
                setattr(subfield, "__sheet_name__", sheet_name)
                setattr(subfield, "__regbank_name__", regbank_name)
                for field in cur_subfield.__field_names__:
                    setattr(subfield, field, getattr(cur_subfield, field))
                setattr(register, subfield_name, subfield)
            setattr(sheet, register_name, register)
    setattr(regbank, sheet_name, sheet)
    db_dict[regbank_name] = regbank

def regbank_load_sheet(regbank_name, sheet_name, 
        base_addr, offset_type=offsets_enum_t.BYTE_OFFSETS, as_sheet_name=None):
    assert regbank_name in regbank_files.keys(), \
            "Regbank file must be loaded before loading sheets"
    try:
        workbook = xlrd.open_workbook(regbank_files[regbank_name])
    except:
        set_trace()
        pass
    assert sheet_name in workbook.sheet_names(), \
            "Loaded regbank doesnt contain sheet specified"
    xl_sheet = workbook.sheet_by_name(sheet_name)
    row_idx = 0
    while row_idx < xl_sheet.nrows:
        text = xl_sheet.row(row_idx)[0].value
        if re.search(regbank_info["start_row_header"], text, re.IGNORECASE):
            row_idx += 1    # Skip first row corresponding to header
            break
        else:
            row_idx += 1
    if row_idx == xl_sheet.nrows:
        assert 0, "Register sheet is an invalid sheet"

    if as_sheet_name:
        assert as_sheet_name not in db[regbank_name].keys()
        sheet_name = as_sheet_name
    db[regbank_name][sheet_name] = sheet_t()
    db[regbank_name][sheet_name].base_addr = base_addr
    db[regbank_name][sheet_name].registers = OrderedDict()
    while 1:
        row_line = xl_sheet.row(row_idx)
        rows = []
        rows.append(xl_sheet.row(row_idx))
        row_idx += 1
        while ((row_idx<xl_sheet.nrows) and 
                (xl_sheet.row(row_idx)[regbank_info["offset_address_col"]].value=='')):
            rows.append(xl_sheet.row(row_idx))
            row_idx += 1
        [register_name, register] = regbank_decode_register(rows)
        if register:
            db[regbank_name][sheet_name].registers[register_name] = register
        if row_idx>=xl_sheet.nrows :
            break
    predicted_offset_type = regbank_offset_size_predict(db[regbank_name][sheet_name])
    assert predicted_offset_type==offset_type, "Predicted offset type" \
            "different from given offset type"
    db[regbank_name][sheet_name].offset_type = offset_type
    db[regbank_name][sheet_name].mmap_done = False
    first_register_name = list(db[regbank_name][sheet_name].registers.keys())[0]
    last_register_name  = list(db[regbank_name][sheet_name].registers.keys())[-1]
    db[regbank_name][sheet_name].start_addr = \
            db[regbank_name][sheet_name].registers[first_register_name].offset_addr * \
            (1 if offset_type==offsets_enum_t.BYTE_OFFSETS else 4) + base_addr
    db[regbank_name][sheet_name].end_addr = \
            db[regbank_name][sheet_name].registers[last_register_name].offset_addr * \
            (1 if offset_type==offsets_enum_t.BYTE_OFFSETS else 4) + base_addr
    regbank_make_struct(regbank_name, sheet_name)
    return [regbank_name, sheet_name]

def regbank_unload_sheet(regbank_name, sheet_name):
    if regbank_name in db.keys():
        if sheet_name in db[regbank_name].keys():
            db[regbank_name].pop(sheet_name)

def regbank_offset_size_predict(sheet):
    diffs = {1:0, 4:0}
    register_names = list(sheet.registers.keys())
    for register_idx in range(len(sheet.registers)-1):
        offset_diff = sheet.registers[register_names[register_idx+1]].offset_addr - \
                sheet.registers[register_names[register_idx]].offset_addr
        if offset_diff in [1, 4]:
            diffs[offset_diff] += 1
    return offsets_enum_t.WORD_OFFSETS if diffs[1] > diffs[4] else offsets_enum_t.BYTE_OFFSETS

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs="+")
    parse_res = parser.parse_args()
    fnames = parse_res.fnames
    regbank_to_load(fnames[0])
    regbank_load_sheet("demo_regbank", "Sheet_A", 0x4000000, offsets_enum_t.WORD_OFFSETS)
    regbank_load_sheet("demo_regbank", "Sheet_A", 0x4000400, offsets_enum_t.WORD_OFFSETS, "Sheet_A_1")

