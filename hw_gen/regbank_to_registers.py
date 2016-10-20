import sys; sys.path.append("../client")
import re
from math import log, ceil
from sys import stdout
from pdb import set_trace
from regbank_to_db import regbank_database_t
from regbank_parser import regbank_t

def generate_regbank_rtl(module):
    module_name = module._module_name + "_regbank"
    rtl_file = open(module_name + ".v", "w")

    base_addr = module._get_base_addr()
    last_addr = list(module._registers_db.values())[-1]._get_addr()
    address_bit_width = ceil(log(last_addr - base_addr + 4, 2))

    tab_space = "    "

    reset_bar_wire = "reset_bar_in"
    clock_wire = "clock_in"
    enable_wire = "enable_in"
    address_wire = "address_in"
    read_data_wire = "read_data_out"
    write_data_wire = "write_data_in"
    read_write_bar_wire = "read_write_bar_in"
    read_complete_wire = "read_complete_out"
    write_complete_wire = "write_complete_out"

    # Write the module signature
    rtl_file.write("module {0} (\n".format(module_name))
    all_io = list([reset_bar_wire, clock_wire, enable_wire, address_wire, read_data_wire,
        write_data_wire, read_write_bar_wire, read_complete_wire, write_complete_wire])
    for idx, io in enumerate(all_io):
        if not re.search('reserved', io, re.I):
            comma = ',' if idx < len(all_io)-1 else ''
            rtl_file.write(1*tab_space + "{0}".format(io) + comma + "\n")
    rtl_file.write(");\n")
    
    # Declare the module registers and wires 
    # Declare standard module registers for Read/Write access
    hw_declaration_string = 1*tab_space + "{0:12s}                {1:>10s} {2};\n"
    
    rtl_file.write(hw_declaration_string.format("input wire", "", reset_bar_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "", clock_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "", enable_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "[{0}:0]".format(address_bit_width-1), address_wire))
    rtl_file.write(hw_declaration_string.format("output reg", "[31:0]", read_data_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "[31:0]", write_data_wire))
    rtl_file.write(hw_declaration_string.format("input wire", "", read_write_bar_wire))
    rtl_file.write(hw_declaration_string.format("output reg", "", read_complete_wire))
    rtl_file.write(hw_declaration_string.format("output reg", "", write_complete_wire))
    rtl_file.write("\n")

    # Declare the module registers according to the regbank definitions

    for register in module:
        for subfield in register:
            if not re.search("reserved", subfield._subfield_name, re.I):
                if re.search("W", subfield._sw_attr, re.I):
                    # SW Writable attribute
                    register_type = "reg"
                else:
                    # SW Readable attribute
                    register_type = "wire"
                if subfield._bit_width>1:
                    bitfield = "[{0:2d}:0]".format(subfield._bit_width-1)
                else:
                    bitfield = ""
                rtl_file.write(hw_declaration_string.format(register_type, bitfield, subfield._subfield_name))
    rtl_file.write("\n")


    # Instantiate the HW module for which regbank module is built
    rtl_file.write(1*tab_space + "{0} u0_{0} (\n".format(module._module_name))

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
            rtl_file.write(2*tab_space + ".{0} ({0})".format(io) + comma + "\n")
    rtl_file.write(1*tab_space + ");\n")
    rtl_file.write("\n")
    
    rtl_file.write(1*tab_space + "reg  state;\n")
    rtl_file.write(1*tab_space + "reg  next_state;\n")
    rtl_file.write(1*tab_space + "localparam IDLE              = 1'd0;\n")
    rtl_file.write(1*tab_space + "localparam READ_WRITE_MODE   = 1'd1;\n")
    rtl_file.write("\n")

    rtl_file.write(1*tab_space + "always @ (posedge clock_in or negedge reset_bar_in) begin\n")
    rtl_file.write(2*tab_space + "if (reset_bar_in==1'b0) begin\n")
    rtl_file.write(3*tab_space + "read_data_out <= 32'd0;\n")
    rtl_file.write(3*tab_space + "read_complete_out <= 1'd0;\n")
    rtl_file.write(3*tab_space + "write_complete_out <= 1'd0;\n")
    rtl_file.write(3*tab_space + "state <= IDLE;\n")
    rtl_file.write(2*tab_space + "end else begin\n")
    rtl_file.write(3*tab_space + "case (state)\n")

    rtl_file.write(4*tab_space + "IDLE: begin\n")
    rtl_file.write(5*tab_space + "if (enable_in) begin\n")
    rtl_file.write(6*tab_space + "state <= READ_WRITE_MODE;\n")
    rtl_file.write(5*tab_space + "end else begin\n")
    rtl_file.write(6*tab_space + "state <= IDLE;\n")
    rtl_file.write(5*tab_space + "end\n")
    rtl_file.write(4*tab_space + "end\n")

    rtl_file.write(4*tab_space + "READ_WRITE_MODE: begin\n")
    rtl_file.write(5*tab_space + "if (read_write_bar_in) begin\n")
    rtl_file.write(6*tab_space + "read_complete_out <= 1'd1;\n")
    rtl_file.write(6*tab_space + "if (!read_complete_out) begin\n");
    rtl_file.write(7*tab_space + "case (address_in) \n")
    for register in module:
        rtl_file.write(8*tab_space + "{0}'d{1}: begin\n".format(address_bit_width, register._get_addr() - module._get_base_addr()))
        rtl_file.write(9*tab_space + "read_data_out <= ")
        subfields_list = []
        for subfield in register:
            if not re.search('reserved', subfield._subfield_name, re.I):
                subfields_list.append("({0}<<{1})".format(subfield._subfield_name, subfield._bit_position[0]))
        rtl_file.write(" | ".join(subfields_list) + ";\n")
        rtl_file.write(8*tab_space + "end\n")
    rtl_file.write(8*tab_space + "default: begin\n")
    rtl_file.write(9*tab_space + "read_data_out <= 32'd0;\n")
    rtl_file.write(8*tab_space + "end\n")
    rtl_file.write(7*tab_space + "endcase\n")
    rtl_file.write(6*tab_space + "end\n");

    rtl_file.write(5*tab_space + "end else begin\n")
    rtl_file.write(6*tab_space + "write_complete_out <= 1'd1;\n")
    rtl_file.write(6*tab_space + "if (!write_complete_out) begin\n");
    rtl_file.write(7*tab_space + "case (address_in) \n")
    for register in module:
        rtl_file.write(8*tab_space + "{0}'d{1}: begin\n".format(address_bit_width, register._get_addr() - module._get_base_addr()))
        for subfield in register:
            
            if not re.search('reserved', subfield._subfield_name, re.I) and re.search("W", subfield._sw_attr, re.I):
                if subfield._bit_width > 1:
                    bitfield = "[{0}:{1}]".format(subfield._bit_position[-1], subfield._bit_position[0])
                else:
                    bitfield = "[{0}]".format(subfield._bit_position[0])
                rtl_file.write(9*tab_space + "{0} <= write_data_in{1};\n".format(subfield._subfield_name, bitfield))
        rtl_file.write(8*tab_space + "end\n")
    rtl_file.write(8*tab_space + "default: begin\n")
    rtl_file.write(8*tab_space + "end\n")
    rtl_file.write(7*tab_space + "endcase\n")
    rtl_file.write(6*tab_space + "end\n");


    rtl_file.write(5*tab_space + "end\n")
    rtl_file.write("\n")
    rtl_file.write(5*tab_space + "if (enable_in) begin\n")
    rtl_file.write(6*tab_space + "state <= READ_WRITE_MODE;\n")
    rtl_file.write(5*tab_space + "end else begin\n")
    rtl_file.write(6*tab_space + "read_complete_out <= 1'd0;\n")
    rtl_file.write(6*tab_space + "write_complete_out <= 1'd0;\n")
    rtl_file.write(6*tab_space + "read_data_out <= 32'd0;\n")
    rtl_file.write("\n")
    rtl_file.write(6*tab_space + "state <= IDLE;\n")
    rtl_file.write(5*tab_space + "end\n")
    rtl_file.write(4*tab_space + "end\n")
    rtl_file.write(3*tab_space + "endcase\n")
    rtl_file.write(2*tab_space + "end\n")
    rtl_file.write(1*tab_space + "end\n")

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
            generate_regbank_rtl(module)
            generated_modules[module._module_name] = 1;

