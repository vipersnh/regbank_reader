import re
import pickle
from os.path import basename, splitext
from pdb import set_trace
from collections import namedtuple, OrderedDict
from StructDict import StructDict
from client import g_client_obj, target_t
import enumeration

g_regbanks = OrderedDict()

class offsets_enum_t(enumeration.Enum):
    BYTE_OFFSETS = 0
    WORD_OFFSETS = 1

subfield_info_t = namedtuple("subfield_info_t", 
        [   "subfield_name", 
            "bit_width", 
            "bit_position", 
            "default_val", 
            "sw_attr", 
            "hw_attr", 
            "description",
            ])

register_info_t = namedtuple("register_info_t",
        [   "register_name",
            "offset_addr",
            "default_val",
            "subfields",
            ])

module_info_t = namedtuple("module_info_t",
        [   "module_name",
            "module_instance_name",
            "base_addr",
            "offset_type",
            "size",
            "registers",
            ])

regbank_info_t = namedtuple("regbank_info_t",
        [   "regbank_name",
            "regbank_file_name",
            "modules",
            ])

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
        self._temp_value_ = 0
        self._initialized = True

    def __dir__(self):
        return ['_value', '_stored_value', '_temp_value']

    def __len__(self):
        return 1

    def __getitem__(self, index):
        return None

    def _update_using_value(self, value, is_temp_value=False):
        if is_temp_value:
            self._temp_value_ = (value & self._bitfield.mask)>>self._bitfield.rshift
        else:
            self._stored_value = (value & self._bitfield.mask)>>self._bitfield.rshift
    
    def __getattr__(self, item):
        if item=='_value':
            self._register._get_hw_value()
            return self._stored_value
        else:
            if self._is_special_attr(item):
                if item=='_temp_value':
                    return self.__dict__['_temp_value_']
                else:
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
                elif item=='_stored_value' or item=='_temp_value_':
                    dict.__setattr__(self, item, value)
                elif item=='_temp_value':
                    self._temp_value_ = value & self._bitfield.value     # Set the subfield value to desired
                    self._register._update_value_from_subfields(is_temp_value=True)   # Form full word from subfields and write to hw 
            else:
                set_trace()
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
        self._temp_value_ = 0
        self._initialized = True

    def __len__(self):
        return len(self._subfields_db)

    def __getitem__(self, index):
        return list(self._subfields_db.values())[index]

    def __dir__(self):
        return list(self._subfields_db.keys()) + ['_value', '_stored_value', '_temp_value']

    def _get_addr(self):
        return self._module_instance._get_base_addr() + \
                self._offset_addr * self._module_instance._get_offset_size()
    
    def _get_offset(self):
        return self._offset_addr * self._module_instance._get_offset_size()

    def _get_hw_value(self):
        value = g_client_obj.read_address(self._get_addr())
        self._update_all_values(value)
        return value
    
    def _set_hw_value(self, value):
        mask = 0
        for subfield in self._subfields_db.values():
            mask |= subfield._bitfield.mask
        value = value & mask
        g_client_obj.write_address(self._get_addr(), value)
        self._update_all_values(value)

    def _update_all_values(self, value, is_temp_value=False):
        if is_temp_value:
            self._temp_value_ = value
            for subfield in self._subfields_db.values():
                subfield._update_using_value(self._temp_value_, True)
        else:
            self._stored_value = value
            for subfield in self._subfields_db.values():
                subfield._update_using_value(self._stored_value, False)

    def _update_value_from_subfields(self, is_temp_value=False):
        value = 0
        for subfield in self._subfields_db.values():
            if is_temp_value:
                value |= subfield._temp_value_<<subfield._bitfield.rshift
            else:
                value |= subfield._stored_value<<subfield._bitfield.rshift
        
        if is_temp_value:
            self._temp_value_ = value
        else:
            self._set_hw_value(value)

    def __getattr__(self, item):
        if item=='_value':
            value = g_client_obj.read_address(self._get_addr())
            self._update_all_values(value)
            return value
        else:
            if self._is_special_attr(item):
                if item=='_temp_value':
                    return self._temp_value_
                else:
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
                elif item=='_stored_value' or item=='_temp_value_':
                    dict.__setattr__(self, item, value)
                elif item=='_temp_value':
                    self._update_all_values(value, True)
                else:
                    set_trace()
                    raise ValueError('This attribute cant be set outside of init')
            else:
                assert item not in self._subfields_db.keys()
                self._subfields_db[item] = value
        else:
            dict.__setattr__(self, item, value)

class module_instance_t(base_t):
    def __init__(self, module_name, module_instance_name, regbank_name, base_address, 
            offset_type):
        self._initialized = False
        self._module_name = module_name
        self._module_instance_name = module_instance_name
        self._regbank_name = regbank_name
        self._base_addr = base_address
        self._offset_type = offset_type
        self._registers_db = OrderedDict()
        self._size = 0
        self._initialized = True

    def _set_size(self, size):
        dict.__setattr__(self, '_size', size)
        

    def __len__(self):
        return len(self._registers_db)

    def __getitem__(self, index):
        return list(self._registers_db.values())[index]

    def __dir__(self):
        return list(self._registers_db.keys())

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
                set_trace()
                raise ValueError('This attribute cant be set outside of init')
            else:
                try:
                    assert item not in self._registers_db.keys()
                except:
                    set_trace()
                self._registers_db[item] = value
        else:
            dict.__setattr__(self, item, value)

    def _get_base_addr(self):
        return self._base_addr

    def _get_offset_size(self):
        return 1 if self._offset_type==offsets_enum_t.BYTE_OFFSETS else 4

class regbank_t:
    def __init__(self, regbank_db_fname):
        if type(regbank_db_fname)==str:
            database = pickle.load(open(regbank_db_fname, "rb"))
            print("Reading register bank database {0}".format(database.regbank_name))
        else:
            database = regbank_db_fname
        self._initialized = False
        self._regbank_name = database.regbank_name
        self._module_instances = OrderedDict()
        self._initialized = True
        self._regbank_load_module_instances_from_database(database)
        g_regbanks[database.regbank_name] = self

    def connect(self, unique_id, unique_msg, timeout):
        print("Connecting to target with unique_id:{0} unique_msg:{1}".format(unique_id, unique_msg))
        return g_client_obj.connect(unique_id, unique_msg, timeout)

    def disconnect(self):
        return g_client_obj.disconnect()

    def rw(self, addr, value=None):
        if value==None:
            # Read command
            # TODO: Handle 64 bit address
            if addr & ~0xFFFFFFFF:
                print("Address is beyond 32 bits")
                return False
            val = g_client_obj.read_address(addr)
            return [val, hex(val), bin(val)]
        else:
            return g_client_obj.write_address(addr, value)

    def read_address(self, addr):
        return g_client_obj.read_address(addr)

    def write_address(self, addr, value):
        return g_client_obj.write_address(addr, value)

    def get_read_sequence(self, addr, comment):
        [register, _] = self.get_write_sequence(addr, 0x00, comment)
        seq = list()
        if comment:
            seq.append("#"+comment)
        if register:
            seq.append("print({0}.{1}.{2}._value) # @ {3}".format(register._regbank_name,
                register._module_instance_name, register._register_name, hex(register._get_addr()), comment))
        else:
            seq.append("{0}.read_address({1})".format(self._regbank_name, hex(addr)))
        return [register, seq]


    def get_write_sequence(self, addr, value, comment=None):
        # Should return a list of python executable statements which functionally represent the same as
        # writing to that addr with value

        seq = list()
        if comment:
            seq.append("#"+comment)

        wr_register = None

        # Find the instance in which the write exists
        for instance in self._module_instances.values():
            if addr >= instance._base_addr and addr < (instance._base_addr + instance._size):
                # Find the register in the current sheet if it is part of that sheet
                for register in instance._registers_db.values():
                    if register._get_addr()==addr:
                        wr_register = register
                        break
            if wr_register:
                break
        
        if wr_register:
            wr_register._temp_value = value
            if 0:
                seq.append("{0}.{1}.{2}._value = {3}    # @ {4} = {3}".format(wr_register._regbank_name,
                    wr_register._module_instance_name, wr_register._register_name,
                    hex(value), hex(wr_register._get_addr())));
            else:
                for subfield in wr_register._subfields_db.values():
                    try:
                        seq.append("{0}.{1}.{2}.{3}._value = {4}    # @ {5} [{6}:{7}] = {4}".format(
                            subfield._regbank_name, subfield._module_instance_name, subfield._register_name,
                            subfield._subfield_name, hex(subfield._temp_value),
                            hex(wr_register._get_addr()), subfield._bit_position[-1],
                            subfield._bit_position[0]))
                    except:
                        set_trace()
                        pass
        else:
            seq.append("{0}.write_address({1}, {2})".format(self._regbank_name, hex(addr), hex(value)))
        
        return [wr_register, seq]


    def __len__(self):
        return len(self._module_instances)

    def __getitem__(self, index):
        return list(self._module_instances.values())[index]

    def __getattr__(self, item):
        if re.search("^_", item):
            return self.__dict__[item]
        else:
            return self._module_instances[item]

    def _regbank_load_module_instances_from_database(self, database):
        unwanted_char_pattern = '[^a-zA-Z0-9 \n\.]'
        regbank_name = database.regbank_name
        regbank_name = re.sub(unwanted_char_pattern, '_', regbank_name)
        for i, (module_instance_name, module_info_instance) in enumerate(database.modules.items()):
            module_instance_name = module_info_instance.module_instance_name
            module_instance_name = re.sub(unwanted_char_pattern, '_', module_instance_name)
            module_name = module_info_instance.module_name
            module_name = re.sub(unwanted_char_pattern, '_', module_name)
            base_addr = module_info_instance.base_addr
            offset_type = module_info_instance.offset_type
            module_instance = module_instance_t(module_info_instance.module_name, 
                                                module_info_instance.module_instance_name, 
                                                regbank_name, 
                                                base_addr, 
                                                offset_type)
            for j, (register_name, register_info_instance) in enumerate(module_info_instance.registers.items()):
                register_name = re.sub(unwanted_char_pattern, '_', register_name)
                register_instance = register_t(module_instance, register_name, module_info_instance.module_instance_name,
                        regbank_name, register_info_instance.offset_addr, 0);
                for k, (subfield_name, subfield_info_instance) in enumerate(register_info_instance.subfields.items()):
                    subfield_name = re.sub(unwanted_char_pattern, '_', subfield_name)
                    subfield = subfield_t(register_instance, subfield_name, register_name, 
                        module_info_instance.module_instance_name, regbank_name, subfield_info_instance.bit_width, 
                        subfield_info_instance.bit_position, 
                        subfield_info_instance.sw_attr, 
                        subfield_info_instance.hw_attr, 
                        subfield_info_instance.default_val, 
                        subfield_info_instance.description);
                    register_instance._subfields_db[subfield_name] = subfield
                module_instance._registers_db[register_name] = register_instance
            self._module_instances[module_info_instance.module_instance_name] = module_instance
            

                
    def __dir__(self):
        return list(self._module_instances.keys())


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

