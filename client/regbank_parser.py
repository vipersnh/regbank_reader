import xlrd
import re
from os.path import basename, splitext
from pdb import set_trace
from collections import namedtuple, OrderedDict
from StructDict import StructDict
import enumeration
from client import client
from math import log2

g_regbanks = OrderedDict()

class offsets_enum_t(enumeration.Enum):
    BYTE_OFFSETS = 0
    WORD_OFFSETS = 1

## Columns information
regbank_modules_info = {"start_row_header"   :"Offset address",
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

regbank_instances_info =  {
      "start_row_header"    : "Module",
      "module_name_col"     : 0,
      "address_bits_col"    : 1,
      "base_address_col"    : 2,
      "offset_size_col"     : 3,
      "instance_name_col"   : 4
    };

class bitfield_t:
    def __init__(self, start=0, end=31):
        self.mask = ((1<<(end+1))) - ((1<<(start)))
        self.rshift = start
        self.value = self.mask >> self.rshift
        self.end   = end
        self.start = start

class base_t:
    def _is_special_attr(self, item):
        if re.search("^_", item):
            return True
        else:
            return False

class subfield_t(base_t):
    def __init__(self, register_ref, subfield_name, register_name, 
            module_instance_name, regbank_name, bit_width, bit_position, 
            sw_attr, hw_attr, default_val, description):
        self._register = register_ref
        self._subfield_name = subfield_name
        self._register_name = register_name
        self._module_instance_name = module_instance_name
        self._regbank_name = regbank_name
        self._bit_width = bit_width
        self._bit_position = bit_position
        self._sw_attr = sw_attr
        self._hw_attr = hw_attr
        self._default_val = default_val
        self._description = description
        if isinstance(default_val, int):
            self._stored_value = default_val
        else:
            self._stored_value = 0
        self._bitfield = bitfield_t(self._bit_position[0], self._bit_position[-1])
        self._initialized = True

    def __len__(self):
        return 1

    def __getitem__(self, index):
        return None

    def _update_using_value(self, value):
        self._stored_value = (value & self._bitfield.mask)>>self._bitfield.rshift
    
    def __getattr__(self, item):
        if item=='_value':
            self._register._get_hw_value()
            return self._stored_value
        else:
            if self._is_special_attr(item):
                return self.__dict__[item]
            else:
                return None

    def __setattr__(self, item, value):
        try:
            initialized = self._initialized
        except:
            initialized = False
        if initialized:
            if self._is_special_attr(item):
                if item=='_value':
                    self._register._get_hw_value() # Update current value
                    self._stored_value = value & self._bitfield.value     # Set the subfield value to desired
                    self._register._update_value_from_subfields()   # Form full word from subfields and write to hw 
                elif item=='_stored_value':
                    dict.__setattr__(self, item, value)
            else:
                raise ValueError('This attribute cant be set outside of init')
        else:
            dict.__setattr__(self, item, value)

class register_t(base_t):
    def __init__(self, module_instance_ref, register_name, module_instance_name, regbank_name, offset_addr, default_val):
        self._initialized = False
        self._module_instance = module_instance_ref
        self._register_name = register_name
        self._module_instance_name = module_instance_name
        self._regbank_name = regbank_name
        self._offset_addr = offset_addr
        self._default_val = default_val
        self._subfields_db = OrderedDict()
        if isinstance(default_val, int):
            self._stored_value = default_val
        else:
            self._stored_value = 0

        self._initialized = True

    def __len__(self):
        return len(self._subfields_db)

    def __getitem__(self, index):
        return list(self._subfields_db.values())[index]

    def __dir__(self):
        return self._subfields_db.keys()

    def _get_addr(self):
        return self._module_instance._get_base_addr() + \
                self._offset_addr * self._module_instance._get_offset_size()
    
    def _get_offset(self):
        return self._offset_addr * self._module_instance._get_offset_size()

    def _get_hw_value(self):
        value = client.read_address(self._get_addr())
        self._update_all_values(value)
        return value
    
    def _set_hw_value(self, value):
        mask = 0
        for subfield in self._subfields_db.values():
            mask |= subfield._bitfield.mask
        value = value & mask
        client.write_address(self._get_addr(), value)
        self._update_all_values(value)

    def _update_all_values(self, value):
        self._stored_value = value
        for subfield in self._subfields_db.values():
            subfield._update_using_value(self._stored_value)

    def _update_value_from_subfields(self):
        value = 0
        for subfield in self._subfields_db.values():
            value |= subfield._stored_value<<subfield._bitfield.rshift
        self._set_hw_value(value)

    def __getattr__(self, item):
        if item=='_value':
            value = client.read_address(self._get_addr())
            self._update_all_values(value)
            return value
        else:
            if self._is_special_attr(item):
                return self.__dict__[item]
            else:
                return self._subfields_db[item]

    def __setattr__(self, item, value):
        try:
            initialized = self._initialized
        except:
            initialized = False
        
        if initialized:
            if self._is_special_attr(item):
                if item=='_value':
                    self._set_hw_value(value)
                elif item=='_stored_value':
                    dict.__setattr__(self, item, value)
                else:
                    raise ValueError('This attribute cant be set outside of init')
            else:
                assert item not in self._subfields_db.keys()
                self._subfields_db[item] = value
        else:
            dict.__setattr__(self, item, value)

class module_instance_t(base_t):
    def __init__(self, module_instance_name, regbank_name, base_address, 
            offset_type):
        self._initialized = False
        self._module_instance_name = module_instance_name
        self._regbank_name = regbank_name
        self._base_addr = base_address
        self._offset_type = offset_type
        self._registers_db = OrderedDict()
        self._initialized = True

    def __len__(self):
        return len(self._registers_db)

    def __getitem__(self, index):
        return list(self._registers_db.values())[index]

    def __dir__(self):
        return self._registers_db.keys()

    def __getattr__(self, item):
        if self._is_special_attr(item):
            return self.__dict__[item]
        else:
            if item in self._registers_db.keys():
                return self._registers_db[item]
            else:
                return None

    def __setattr__(self, item, value):
        try:
            initialized = self._initialized
        except:
            initialized = False
        if initialized:
            if self._is_special_attr(item):
                raise ValueError('This attribute cant be set outside of init')
            else:
                assert item not in self._registers_db.keys()
                self._registers_db[item] = value
        else:
            dict.__setattr__(self, item, value)

    def _get_base_addr(self):
        return self._base_addr

    def _get_offset_size(self):
        return 1 if self._offset_type==offsets_enum_t.BYTE_OFFSETS else 4

class regbank_t:
    def __init__(self, regbank_file_name, regbank_name):
        self._initialized = False
        self._regbank_name = regbank_name
        self._regbank_file_name = regbank_file_name
        self._module_instances = OrderedDict()
        self._initialized = True
        self._regbank_load_module_instances()
        g_regbanks[regbank_name] = self

    def __len__(self):
        return len(self._module_instances)

    def __getitem__(self, index):
        return list(self._module_instances.values())[index]

    def __getattr__(self, item):
        if re.search("^_", item):
            return self.__dict__[item]
        else:
            return self._module_instances[item]

    def _is_sheet_valid_module(sheet_name):
        workbook = xlrd.open_workbook(self._regbank_file_name)
        xl_sheet = workbook.sheet_by_name(sheet_name)
        row_idx = 0
        while row_idx < xl_sheet.nrows:
            text = xl_sheet.row(row_idx)[0].value
            if re.search(regbank_modules_info["start_row_header"], 
                    text, re.IGNORECASE):
                row_idx += 1    # Skip first row corresponding to header
                break
            else:
                row_idx += 1
        if row_idx == xl_sheet.nrows:
            return False
        else:
            return True

    def _regbank_offset_size_predict(module_instance_ref):
        assert 0
        diffs = {1:0, 4:0}
        register_names = list(sheet.registers.keys())
        for register_idx in range(len(sheet.registers)-1):
            offset_diff =  \
                sheet.registers[register_names[register_idx+1]].offset_addr - \
                sheet.registers[register_names[register_idx]].offset_addr
            if offset_diff in [1, 4]:
                diffs[offset_diff] += 1
        return offsets_enum_t.WORD_OFFSETS \
            if diffs[1] > diffs[4] else offsets_enum_t.BYTE_OFFSETS


    def _regbank_decode_rows_to_register(self, rows, module_instance_ref, 
            module_instance_name, regbank_name) :
        register_name = rows[0][regbank_modules_info["register_name_col"]].value
        offset_addr =int(rows[0][regbank_modules_info["offset_address_col"]].value)
        register = register_t(module_instance_ref, register_name, module_instance_name, 
            regbank_name, offset_addr, 0);
        reserved_idx = 0
        for row in rows :
            is_reserved = False
            sw_attr = row[regbank_modules_info["sw_attr_col"]].value
            hw_attr = row[regbank_modules_info["hw_attr_col"]].value
            subfield_name = row[regbank_modules_info["sub_field_name_col"]].value
            bit_width = int(row[regbank_modules_info["bit_width_col"]].value)
            bit_position = row[regbank_modules_info["bit_position_col"]].value
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
                    int(row[regbank_modules_info["default_value_col"]].value, 0)
            except:
                default_val = 0
            description = description = \
                row[regbank_modules_info["description_col"]].value
            if re.search(regbank_modules_info["reserved_keyword"], subfield_name, 
                    re.IGNORECASE):
                subfield_name = regbank_modules_info["reserved_keyword"] + \
                    str(reserved_idx)
                reserved_idx += 1
                is_reserved = True
            try:
                assert subfield_name not in dir(register), \
                "Subfield name already present"
            except:
                set_trace()
                pass
            if not is_reserved:
                setattr(register, subfield_name, 
                    subfield_t(register, subfield_name, register_name, 
                    module_instance_name, regbank_name, bit_width, bit_position, 
                    sw_attr, hw_attr, default_val, description));
        if register_name=='':
            return [None, None]
        else:
            return [register_name, register];

    def _regbank_get_module_instance(self, module_name, base_addr, offset_type, 
            module_instance_name):
        workbook = xlrd.open_workbook(self._regbank_file_name)
        xl_sheet = workbook.sheet_by_name(module_name)
        row_idx = 0
        while row_idx < xl_sheet.nrows:
            text = xl_sheet.row(row_idx)[0].value
            if re.search(regbank_modules_info["start_row_header"], text, 
                    re.IGNORECASE):
                row_idx += 1    # Skip first row corresponding to header
                break
            else:
                row_idx += 1
        if row_idx == xl_sheet.nrows:
            assert 0, "Invalid sheet"

        module_instance = module_instance_t(module_instance_name, 
            self._regbank_name, base_addr, offset_type)

        while 1:
            row_line = xl_sheet.row(row_idx)
            rows = []
            rows.append(xl_sheet.row(row_idx))
            row_idx += 1
            while ((row_idx<xl_sheet.nrows) and 
                    (xl_sheet.row(row_idx)[regbank_modules_info["offset_address_col"]].value=='')):
                rows.append(xl_sheet.row(row_idx))
                row_idx += 1
            [register_name, register] = \
                self._regbank_decode_rows_to_register(rows, module_instance,
                        module_instance_name, self._regbank_name)
            if register:
                setattr(module_instance, register_name, register)
            if row_idx>=xl_sheet.nrows :
                break
        return module_instance

    def _regbank_load_module_instances(self):
        instance_sheet_name = "top_instances_map"
        workbook = xlrd.open_workbook(self._regbank_file_name)

        assert instance_sheet_name in workbook.sheet_names(), "Top Level Instances sheet not found"
        
        xl_sheet = workbook.sheet_by_name(instance_sheet_name)
        row_idx = 0
        while row_idx < xl_sheet.nrows:
            text = xl_sheet.row(row_idx)[0].value
            if re.search(regbank_instances_info["start_row_header"], text, re.IGNORECASE):
                row_idx += 1    # Skip first row corresponding to header
                break
            else:
                row_idx += 1
        if row_idx == xl_sheet.nrows:
            assert 0, "Invalid sheet"

        while row_idx < xl_sheet.nrows:
            module_name = str(xl_sheet.row(row_idx)[regbank_instances_info["module_name_col"]].value)
            if module_name=='':
                break

            address_bits = int(float(str(xl_sheet.row(row_idx)[regbank_instances_info["address_bits_col"]].value)))
            base_address = int(str(xl_sheet.row(row_idx)[regbank_instances_info["base_address_col"]].value), 0)
            offset_size = int(float(str(xl_sheet.row(row_idx)[regbank_instances_info["offset_size_col"]].value)))
            module_instance_name = str(xl_sheet.row(row_idx)[regbank_instances_info["instance_name_col"]].value)

            row_idx += 1
            
            assert module_instance_name not in self._module_instances.keys()
            
            # Use the instance information to load sheets
            module_instance = self._regbank_get_module_instance(module_name,
                    base_address, offsets_enum_t.WORD_OFFSETS if offset_size==4 
                    else offsets_enum_t.BYTE_OFFSETS, module_instance_name)
            self._module_instances[module_instance_name] = module_instance

    def __dir__(self):
        return self._module_instances.keys()


if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs="+")
    parse_res = parser.parse_args()
    fnames = parse_res.fnames
    demo = regbank_t(fnames[0], "demo")
    demo.Sheet_A0.Register_A._value
    set_trace()
    pass

