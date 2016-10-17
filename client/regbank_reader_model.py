from PyQt4.QtCore import QObject, pyqtSignal, QThread, QMutex, Qt, qDebug
from PyQt4.QtGui import QMessageBox
from collections import namedtuple
from pdb import set_trace
from regbank_parser import offsets_enum_t, regbank_t, g_regbanks
from client import g_client_obj, target_t
from os.path import dirname
from sys import exit
from StructDict import StructDict
import time
import re
import os
import types
import code

global_env   = dict()

class regbank_reader_model_t (QObject):
    # Signals
    signal_target_connected = pyqtSignal(target_t)
    signal_target_disconnected = pyqtSignal()
    signal_tib_file_loaded = pyqtSignal(str)
    signal_regbank_file_loaded = pyqtSignal(str)
    signal_tib_exec_op = pyqtSignal(list)
    signal_regbank_updated = pyqtSignal()

    target_search_thread = None

    def __init__(self, tib_file=None, cmd_line=False):
        super(regbank_reader_model_t, self).__init__()
        self.target_search_enabled = False
        self.recording_enabled = False
        self.record_sequence = list()
        self.regbank_load_sequence = list()
        self.client = g_client_obj
        self.target = None
        self.target_connected = False
        self.cmd_line = cmd_line
        self.tib_file = tib_file
        self.server_unique_id = None
        self.server_unique_msg = None
        self.db = g_regbanks

    def load_regbank(self, regbank_file):
        if re.search("^\.", regbank_file):
            try:
                regbank_file = dirname(model.tib_file) + "/" + regbank_file
            except:
                set_trace()
        regbank_name = regbank_file.split('/')[-1].split('.')[0]            
        temp = regbank_t(regbank_file, regbank_name)
        self.signal_regbank_updated.emit()

    def start_recording(self):
        self.recording_enabled = True
        del self.record_sequence[:]

    def stop_recording(self):
        self.recording_enabled = False

    def get_recording(self):
        return self.regbank_load_sequence + self.record_sequence

    def initialize(self):
        self.target_search_thread = QThread()
        self.target_search_thread.started.connect(self.target_search, 
                Qt.DirectConnection)
        self.target_search_thread.start()

        # Process the supplied tib_file if any
        if self.tib_file:
            parse_tib_file(self.tib_file)

    def target_search(self):
        print("Target search thread started")
        count = 0
        while (1):
            if self.target_search_enabled:
                if self.client.connect(self.server_unique_id, self.server_unique_msg, 1):
                    self.connected_to_target(self.client.target)
            elif not self.target_connected and self.target_search_enabled:
                count += 1
                print("No server found, please start the server. {0} timeouts".format(count))
            else:
                time.sleep(1)

    def update_target_search(self, server_unique_id, server_unique_msg):
        self.server_unique_id = server_unique_id
        self.server_unique_msg = server_unique_msg

    def set_target_search_enabled(self, flag):
        self.target_search_enabled = flag

    def connected_to_target(self, target):
        if self.target==None:
            record = "connect({0}, \"{1}\")".format(hex(target.unique_id), target.unique_msg)
            self.regbank_load_sequence.append(record)
            self.target = target
            self.target_connected = True
            self.target = target
            self.signal_target_connected.emit(target)

    def disconnect_from_target(self):
        print("Disconnected from target")
        self.target_connected = False
        self.target = None
        self.client.disconnect()
        self.signal_target_disconnected.emit()


    def display_read_register(self, regbank_name, sheet_name, register_name, subfield_name, value):
        print("Reading {0}.{1}.{2} => ".format(regbank_name, sheet_name, register_name))
        if subfield_name:
            subfield = self.db[regbank_name][sheet_name].registers[register_name].subfields[subfield_name]
            print("    * .{0} [{1}:{2}] = {3}".format(subfield.name, subfield.bit_position[-1], 
                    subfield.bit_position[0], value))
        else:
            for (key, subfield) in self.db[regbank_name][sheet_name].registers[register_name].subfields.items():
                subfield_value = regbank_parser.regbank_get_subfield_value(subfield, value)
                print("    .{0:<20} {{{1:>2}:{2:>2}}} = {3}".format(subfield.name, subfield.bit_position[-1],
                        subfield.bit_position[0], subfield_value))

    def read_register(self, regbank_name, sheet_name, register_name, subfield_name):
        try:
            sheet = self.db[regbank_name][sheet_name]
            register = sheet.registers[register_name]
            addr = sheet.base_addr + register.offset_addr * \
                    (1 if sheet.offset_type==offsets_enum_t.BYTE_OFFSETS else 4)
            read_value = self.read_address(addr)
            if subfield_name:
                subfield = register.subfields[subfield_name]
                bitfield = get_bitfield_spec(subfield.bit_position[0], subfield.bit_position[-1])
                read_value = (read_value & bitfield.mask) >> bitfield.rshift
            return read_value
        except:
            set_trace()
            pass

    def write_register(self, regbank_name, sheet_name, register_name, subfield_name, write_value):
        try:
            sheet = self.db[regbank_name][sheet_name]
            register = sheet.registers[register_name]
            addr = sheet.base_addr + register.offset_addr * \
                    (1 if sheet.offset_type==offsets_enum_t.BYTE_OFFSETS else 4)
            if self.recording_enabled:
                record = "write({0}.{1}.{2}".format(regbank_name, sheet_name, register_name)
                if subfield_name:
                    record += ".{0}".format(subfield_name)
                record += ", {0})".format(hex(write_value))

            if subfield_name:
                subfield = register.subfields[subfield_name]
                bitfield = get_bitfield_spec(subfield.bit_position[0], subfield.bit_position[-1])
                read_value = model.read_register(regbank_name, sheet_name, register_name, subfield_name)
                read_value &= bitfield.mask
                assert (write_value <= bitfield.value), "Number given is larger than bitfield specification"
                write_value = read_value | (write_value << bitfield.rshift)
            
            if self.recording_enabled:
                record += "    # write({0}, {1})".format(hex(addr), hex(write_value))
                self.record_sequence.append(record)

            return self.write_address(addr, write_value)
        except:
            set_trace()
            pass

    def read_address(self, address):
        return self.client.read_address(address)

    def write_address(self, addr, write_value):
        return self.client.write_address(address, value)

    def get_sheet_offsets(self, regbank_name, sheet_name):
        as_sheet_name = "__dummy__"
        regbank_parser.regbank_load_sheet(regbank_name, sheet_name, 0x00, as_sheet_name=as_sheet_name)
        predicted_offset = regbank_parser.regbank_offset_size_predict(
            self.db[regbank_name][as_sheet_name])
        regbank_parser.regbank_unload_sheet(regbank_name, as_sheet_name)
        return predicted_offset


model = regbank_reader_model_t()

def parse_tib_file(tib_file):
    global model
    initialize()
    tib_file_path = dirname(tib_file)

    if not model.target_connected and not model.cmd_line:
        assert 0, "Target must be connected before parsing tib file"

    with open(tib_file, "r") as f:
        script = ""
        for tib in f:
            script += tib
            try:
                co = code.compile_command(script, "<stdin>", "exec")
            except SyntaxError:
                print("SyntaxError in line : {0}".format(tib));
            except OverflowError:
                print("OverflowError in line : {0}".format(tib));
            except ValueError:
                print("ValueError in line : {0}".format(tib));
            if co:
                exec_tib(script, co)
                script = ""
    print("")
    model.signal_tib_file_loaded.emit(tib_file)        

def initialize():
    global_env["model"] = model
    for (key, value) in globals().items():
        if type(value)==types.FunctionType:
            global_env[key] = value
    def _print_(str_in):
        try:
            str_in = str(str_in)
        except:
            assert 0, "Invalid input to print"

        global_env["_print_buf_"].append(str_in)
    global_env["print"] = _print_


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

def exec_tib(exec_lines, co):
    for (key, value) in regbank_parser.db_dict.items():
        if key not in global_env.keys():
            global_env[key] = value
    global_env["_print_buf_"] = list()
    try:
        exec(co, global_env)
        if model.cmd_line:
                print(exec_lines, end='')
        else:
            model.signal_tib_exec_op.emit([exec_lines])
    except:
        set_trace()
        exec(co, global_env) # Execute on break to see error
    if model.cmd_line:
        if len(global_env["_print_buf_"]):
            for i in global_env["_print_buf_"]:
                print("Outp: {0}".format(i))
    else:
        model.signal_tib_exec_op.emit(global_env["_print_buf_"])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fnames', nargs="+")
    parse_res = parser.parse_args()
    fnames = parse_res.fnames
    if fnames[0]:
        cmd_line = True
    else:
        cmd_line = False
    model.cmd_line = cmd_line
    if (fnames[0]) :
        model.tib_file = fnames[0]
    if cmd_line:
        parse_tib_file(fnames[0])



