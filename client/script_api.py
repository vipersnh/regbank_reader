from regbank_reader_model import target_t, model

def connect(ip_addr, port, prot):
    global model
    target = target_t(ip_addr, port, prot, 0)
    model.connect_to_target(target)


def load_regbank(regbank_file):
    global model
    if re.search("^.", regbank_file):
        regbank_file = dirname(model.tib_file) + "/" + regbank_file
    regbank_parser.regbank_load_excel(regbank_file)

def unload_regbank(name):
    pass

def load_sheet(regbank_sheet, base_addr, 
        offset_size, as_sheet=None):
    offset_type = offsets_enum_t.BYTE_OFFSETS if offset_size==1 else \
        offsets_enum_t.WORD_OFFSETS
    regbank_name = regbank_sheet.__regbank_name__
    sheet_name   = regbank_sheet.__sheet_name__
    regbank_parser.regbank_load_sheet(regbank_name, sheet_name, base_addr,
        offset_type, as_sheet)

def unload_sheet(name):
    pass

def read(read_from, bitmask=None):
    if bitmask:
        bitfield = get_bitfield_spec(bitmask[-1], bitmask[0])
    else:
        bitfield = get_bitfield_spec()
    if type(read_from)==int:
        # Read from address specified
        value = model.read_address(read_from)
        return (value & bitfield.mask) >> bitfield.rshift
    else:
        # Read from register specified
        regbank_name  = read_from.__regbank_name__
        sheet_name    = read_from.__sheet_name__
        register_name = read_from.__register_name__
        try:
            subfield_name = read_from.__subfield_name__
        except:
            subfield_name = None
        value = model.read_register(regbank_name, sheet_name, register_name, subfield_name)
        return (value & bitfield.mask) >> bitfield.rshift

def write(write_to, write_value, bitmask=None):
    if bitmask:
        bitfield = get_bitfield_spec(bitmask[-1], bitmask[0])
    else:
        bitfield = get_bitfield_spec()
    if type(write_to)==int:
        if bitmask:
            # Read modify and write sequence
            read_value = read(write_to)
            read_value &= bitfield.mask
            assert (write_value <= bitfield.value), "Number given is larger than bitfield specification"
            write_value = read_value | (write_value << bitfield.rshift)
            model.write_address(write_to, write_value)
        else:
            # Full register write sequence
            model.write_address(write_to, write_value)
    else:
        # Write to specified register
        regbank_name  = write_to.__regbank_name__
        sheet_name    = write_to.__sheet_name__
        register_name = write_to.__register_name__
        try:
            subfield_name = write_to.__subfield_name__
        except:
            subfield_name = None
        write_value = (write_value & bitfield.mask) >> bitfield.rshift
        model.write_register(regbank_name, sheet_name, register_name, subfield_name, write_value)


