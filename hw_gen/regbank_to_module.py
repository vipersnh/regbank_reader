import sys; sys.path.append("../client")
import re
from sys import stdout
from pdb import set_trace
from regbank_to_db import regbank_database_t
from regbank_parser import regbank_t

def generate_module_rtl(module):
    module_name = module._module_name

    rtl_file = open(module_name + ".v", "w")

    tab_space = "    "

    # Write the module signature
    rtl_file.write("module {0} (\n".format(module_name))
    all_io = list()
    nrst_wire = "reset_bar_in"
    clk_wire =  "clock_in"
    all_io.append(nrst_wire)
    all_io.append(clk_wire)

    for register in module:
        for subfield in register:
            all_io.append(subfield._subfield_name)
    
    for idx, io in enumerate(all_io):
        if not re.search('reserved', io, re.I):
            comma = ',' if idx < len(all_io)-1 else ''
            rtl_file.write(1*tab_space + "{0}".format(io) + comma + "\n")
    rtl_file.write(");\n")

    hw_declaration_string = 1*tab_space + "{0:12s}                {1:>10s} {2};\n"

    rtl_file.write(hw_declaration_string.format("input wire", "", nrst_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "", clk_wire))

    for register in module:
        for subfield in register:
            if not re.search("reserved", subfield._subfield_name, re.I):
                if re.search("W", subfield._hw_attr, re.I):
                    # HW Writable attribute
                    register_type = "output reg"
                else:
                    # HW Readable attribute
                    register_type = "input wire"
                if subfield._bit_width>1:
                    bitfield = "[{0:2d}:0]".format(subfield._bit_width-1)
                else:
                    bitfield = ""
                    
                rtl_file.write(hw_declaration_string.format(register_type, bitfield, subfield._subfield_name))

    rtl_file.write("\n\n\n")
    rtl_file.write(1*tab_space + "/* Write user code here */")
    rtl_file.write("\n\n\n")

    rtl_file.write("endmodule\n")
    rtl_file.close()
    

if __name__ =="__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs=1)
    parse_res = parser.parse_args()
    regbank_xl_fname = parse_res.fnames[0]

    db_gen = regbank_database_t(regbank_xl_fname, "module")
    database = db_gen.generate_regbank_database()
    regbank = regbank_t(database)

    generated_modules = {}
    for module in regbank:
        if module._module_name not in generated_modules.keys():
            generate_module_rtl(module)
            generated_modules[module._module_name] = 1;

