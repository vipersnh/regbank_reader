import re
import pickle
from pdb import set_trace
from xlrd import open_workbook
from collections import namedtuple, OrderedDict
from regbank_parser import subfield_info_t, register_info_t, module_info_t, regbank_info_t, offsets_enum_t

class regbank_database_t:
    def __init__(self, regbank_file_name, regbank_name):
        self.file_name = regbank_file_name
        self.name = regbank_name
        self.workbook = open_workbook(self.file_name)
        self.regbank_database = None
        self.regbank_instances_info =  {
              "start_row_header"    : "Module",
              "module_name_col"     : 0,
              "address_bits_col"    : 1,
              "base_address_col"    : 2,
              "offset_size_col"     : 3,
              "instance_name_col"   : 4
            };
        self.regbank_modules_info = {"start_row_header"   :"Offset address",
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

        
    
    def generate_regbank_database(self):
        self.regbank_database = OrderedDict()
        instance_sheet_name = "top_instances_map"
        assert instance_sheet_name in self.workbook.sheet_names(), "Top Level Instances sheet not found"
        xl_sheet = self.workbook.sheet_by_name(instance_sheet_name)
        row_idx = 0
        while row_idx < xl_sheet.nrows:
            text = xl_sheet.row(row_idx)[0].value
            if re.search(self.regbank_instances_info["start_row_header"], text, re.IGNORECASE):
                row_idx += 1    # Skip first row corresponding to header
                break
            else:
                row_idx += 1
        if row_idx == xl_sheet.nrows:
            assert 0, "Invalid sheet"
        modules = OrderedDict()
        while row_idx < xl_sheet.nrows:
            module_name = str(xl_sheet.row(row_idx)[self.regbank_instances_info["module_name_col"]].value)
            if module_name=='':
                break
            address_bits = int(float(str(xl_sheet.row(row_idx)[self.regbank_instances_info["address_bits_col"]].value)))
            base_addr = int(str(xl_sheet.row(row_idx)[self.regbank_instances_info["base_address_col"]].value), 0)
            offset_size = int(float(str(xl_sheet.row(row_idx)[self.regbank_instances_info["offset_size_col"]].value)))
            module_instance_name = str(xl_sheet.row(row_idx)[self.regbank_instances_info["instance_name_col"]].value)

            # Use the instance information to load sheets
            module_registers = self.get_module_registers(module_name, base_addr, 
                    offsets_enum_t.WORD_OFFSETS if offset_size==4 else offsets_enum_t.BYTE_OFFSETS, 
                    module_instance_name)

            modules[module_instance_name] = module_info_t(
                    module_name = module_name,
                    module_instance_name = module_instance_name,
                    base_addr = base_addr,
                    offset_type = offsets_enum_t.WORD_OFFSETS if offset_size==4 else offsets_enum_t.BYTE_OFFSETS,
                    size = offset_size,
                    registers = module_registers)
            row_idx += 1
        self.database = regbank_info_t(
                regbank_name = self.name,
                regbank_file_name = self.file_name,
                modules = modules)
        return self.database

    def get_module_registers(self, module_name, base_addr, offset_type, module_instance_name):
        registers = OrderedDict()

        xl_sheet = self.workbook.sheet_by_name(module_name)
        row_idx = 0
        while row_idx < xl_sheet.nrows:
            text = xl_sheet.row(row_idx)[0].value
            if type(text)!=str:
                text = "{0}".format(int(text))
            if re.search(self.regbank_modules_info["start_row_header"], text, 
                    re.IGNORECASE):
                row_idx += 1    # Skip first row corresponding to header
                break
            else:
                row_idx += 1
        if row_idx == xl_sheet.nrows:
            set_trace()
            assert 0, "Invalid sheet"

        reserved_register_idx = 0
        while 1:
            row_line = xl_sheet.row(row_idx)
            rows = []
            rows.append(xl_sheet.row(row_idx))
            row_idx += 1
            while ((row_idx<xl_sheet.nrows) and 
                    (xl_sheet.row(row_idx)[self.regbank_modules_info["offset_address_col"]].value=='')):
                rows.append(xl_sheet.row(row_idx))
                row_idx += 1
            
            # Decode into registers and subfields
            register_name = rows[0][self.regbank_modules_info["register_name_col"]].value
            offset_addr =int(rows[0][self.regbank_modules_info["offset_address_col"]].value)

            if register_name=="Reserved" or register_name=='RESERVED':
                register_name = "RESERVED{0}".format(reserved_register_idx)
                reserved_register_idx += 1
 
            [reserved_register_idx, register] = self.get_decoded_register(rows, reserved_register_idx)

            if register:
                registers[register_name] = register
            if row_idx>=xl_sheet.nrows :
                break
        return registers

    def get_decoded_register(self, rows, reserved_register_idx):
        register_name = rows[0][self.regbank_modules_info["register_name_col"]].value
        offset_addr =int(rows[0][self.regbank_modules_info["offset_address_col"]].value)

        if register_name=="Reserved" or register_name=='RESERVED':
            register_name = "RESERVED{0}".format(reserved_register_idx)
            reserved_register_idx += 1

        subfields = OrderedDict()

        reserved_subfield_idx = 0
        for row in rows :
            is_reserved = False
            sw_attr = row[self.regbank_modules_info["sw_attr_col"]].value
            hw_attr = row[self.regbank_modules_info["hw_attr_col"]].value
            subfield_name = row[self.regbank_modules_info["sub_field_name_col"]].value
            bit_width = int(row[self.regbank_modules_info["bit_width_col"]].value)
            bit_position = row[self.regbank_modules_info["bit_position_col"]].value
            assert 'x' not in bit_position, "Invalid x in bit_position field"
            if ':' in bit_position:
                [end, start] = re.findall("\d+", bit_position)
            else:
                [start] = re.findall("\d+", bit_position)
                end = start
            start = int(start, 0); end = int(end, 0)
            bit_position = list(range(start, end+1))
            sw_attr = sw_attr
            hw_attr = hw_attr
            try:
                default_val = \
                    int(row[self.regbank_modules_info["default_value_col"]].value, 0)
            except:
                default_val = 0
            description = description = \
                row[self.regbank_modules_info["description_col"]].value
            if re.search(self.regbank_modules_info["reserved_keyword"], subfield_name, 
                    re.IGNORECASE):
                subfield_name = self.regbank_modules_info["reserved_keyword"] + \
                    str(reserved_subfield_idx)
                reserved_subfield_idx += 1
            try:
                assert subfield_name not in subfields.keys(), \
                "Subfield name already present"
            except:
                set_trace()
                pass
            subfields[subfield_name] = subfield_info_t(
                    subfield_name = subfield_name,
                    bit_width = bit_width,
                    bit_position = bit_position,
                    default_val = default_val,
                    sw_attr = sw_attr,
                    hw_attr = hw_attr,
                    description = description)
        if register_name=='':
            return [reserved_register_idx, None]
        else:
            register = register_info_t(
                    register_name = register_name,
                    offset_addr = offset_addr,
                    default_val = 0x00,
                    subfields = subfields);
            return [reserved_register_idx, register]

if __name__ =="__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs=1)
    parser.add_argument('regbank_name', nargs=1)
    parser.add_argument('db_fname', nargs=1)
    parse_res = parser.parse_args()
    regbank_xl_fname = parse_res.fnames[0]
    regbank_name = parse_res.regbank_name[0]
    database_file_name= parse_res.db_fname[0]

    db_gen = regbank_database_t(regbank_xl_fname, regbank_name)
    database = db_gen.generate_regbank_database()

    f_database = open(database_file_name, "wb")
    pickle.dump(database, f_database)
    f_database.close()
