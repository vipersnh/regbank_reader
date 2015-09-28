from PyQt4.QtCore import QObject, pyqtSignal, QThread, QMutex, Qt, qDebug
from PyQt4.QtGui import QMessageBox
from collections import namedtuple
from regbank_parser import offsets_enum_t
import regbank_parser
from client import *
from os.path import dirname
from sys import exit
from StructDict import StructDict
import time
import re
import os
import types
import code

target_t     = namedtuple("target_t", ["ip_addr", "port", "protocol",
                                       "max_msg_len", "unique_id", "unique_msg"])
bitfield_t   = StructDict("bitfield_t", ["value", "mask", 
                                         "rshift", "end",
                                         "start"])
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
    keep_alive_thread = None

    def __init__(self, tib_file=None, cmd_line=False, server_udp_port=2222):
        super(regbank_reader_model_t, self).__init__()
        self.db = regbank_parser.db # Reference to actual database
        self.target_search_enabled = False
        self.recording_enabled = False
        self.record_sequence = list()
        self.regbank_load_sequence = list()
        self.client = client_t(server_udp_port)
        self.target = None
        self.target_connected = False
        self.cmd_line = cmd_line
        self.tib_file = tib_file

    def start_recording(self):
        self.recording_enabled = True
        del self.record_sequence[:]

    def stop_recording(self):
        self.recording_enabled = False

    def get_recording(self):
        return self.regbank_load_sequence + self.record_sequence

    def initialize(self):
        self.db_dict = regbank_parser.db_dict
        self.target_search_thread = QThread()
        self.target_search_thread.started.connect(self.target_search, 
                Qt.DirectConnection)
        self.target_search_thread.start()
        self.keep_alive_thread = QThread()
        self.keep_alive_thread.started.connect(self.keep_alive, 
                Qt.DirectConnection)
        self.keep_alive_thread.start()

        # Process the supplied tib_file if any
        if self.tib_file:
            parse_tib_file(self.tib_file)

    def add_new_target(self ,target):
        if self.target==None:
            record = "connect({0}, \"{1}\")".format(hex(target.unique_id), target.unique_msg)
            self.regbank_load_sequence.append(record)
            self.target = target
            self.connect_to_target(target)
        
    def target_search(self):
        print("Target search thread started")
        count = 0
        while (1):
            msg = self.client.get_udp_message()
            if msg and self.target_search_enabled:
                [protocol, ip_addr, port, max_msg_len, server_unique_id, server_unique_msg] = msg;
                target = target_t(ip_addr, port, protocol, max_msg_len, int(server_unique_id, 0), server_unique_msg)
                self.add_new_target(target)
            elif self.target_search_enabled:
                count += 1
                print("No server found, please start the server. {0} timeouts".format(count))
            else:
                time.sleep(1)

    def keep_alive(self):
        print("Keep alive thread started")
        while(1):
            self.keep_alive_thread.sleep(10)
            if self.target_connected:
                msg_write = msg_req_t()
                msg_write.handle = 0xABCDFABC
                msg_write.req_type = KEEP_ALIVE_REQ
                msg_write.addr = 0x00
                msg_write.value = 0x00
                resp = self.client.query_server(msg_write)

    def update_target_search(self, server_unique_id, server_unique_msg):
        self.client.set_server_id(server_unique_id)
        self.client.set_server_msg(server_unique_msg)

    def set_target_search_enabled(self, flag):
        self.target_search_enabled = flag

    def connect_to_target(self, target):
        self.target_connected = True
        self.target = target
        self.client.connect_to_server([target.protocol, target.ip_addr, 
                target.port, target.max_msg_len])
        self.signal_target_connected.emit(target)

    def disconnect_from_target(self):
        self.target_connected = False
        self.target = None
        self.client.disconnect_server()
        self.signal_target_disconnected.emit()

    def read_address(self, address):
        if __debug__:
            return 0xABCDEFAB
        msg_read = msg_req_t()
        msg_read.handle = id(address)
        msg_read.req_type = WORD_READ_REQ
        msg_read.addr = address
        resp = self.client.query_server(msg_read)
        assert(resp.handle==msg_read.handle)
        if resp.status==STATUS_OK:
            assert resp.value != None, "Invalid state"
            return resp.value; # Read success
        else:
            set_trace()
            pass
            return None;       # Read failed

    def write_address(self, address, value):
        if __debug__:
            return True
        msg_write = msg_req_t()
        msg_write.handle = id(address)
        msg_write.req_type = WORD_WRITE_REQ
        msg_write.addr = address
        msg_write.value = value
        resp = self.client.query_server(msg_write)
        assert(resp.handle==msg_write.handle)
        if resp.status==STATUS_OK:
            return True; # Write success
        else:
            return False; # Write failed

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

    def get_sheet_offsets(self, regbank_name, sheet_name):
        as_sheet_name = "__dummy__"
        regbank_parser.regbank_load_sheet(regbank_name, sheet_name, 0x00, as_sheet_name=as_sheet_name)
        predicted_offset = regbank_parser.regbank_offset_size_predict(
            self.db[regbank_name][as_sheet_name])
        regbank_parser.regbank_unload_sheet(regbank_name, as_sheet_name)
        return predicted_offset


model = regbank_reader_model_t()

def get_bitfield_spec(start=0, end=31):
    bitfield = bitfield_t()
    bitfield.mask = ((1<<(end+1))) - ((1<<(start)))
    bitfield.rshift = start
    bitfield.value = bitfield.mask >> bitfield.rshift
    bitfield.end   = end
    bitfield.start = start
    return bitfield
    

def parse_tib(tib, tib_file):
    global model
    if model.cmd_line and not model.target_connected:
        if re.search(" *connect", tib):
            # Connect to target specified
            tib = tib.replace("connect", '')
            [ip_port, protocol] = tib.split("over")
            [ip, port] = ip_port.replace(' ', '').split(':')
            target = target_t(ip, port, protocol, 0)
            model.connect_to_target(target)
            return
        else:
            print("\"connect\" command not found when using command line execution")
            exit(0)
    
    if hasattr(parse_tib, "cur_tib_idx"):
        parse_tib.cur_tib_idx += 1
    else:
        parse_tib.cur_tib_idx  = 0 
    
    print("Executing tib {0}".format(parse_tib.cur_tib_idx))
    bitfield = get_bitfield_spec(0, 31)
    if re.search("\[.*\]", tib):
        bitfield_str = re.split(" *\]", re.split(" *\[ *", tib)[1])[0]
        if re.search(':', bitfield_str):
            [end, start] = re.split(' *: *', bitfield_str)
            end = int(end)
            start = int(start)
        else:
            start = end = int(bitfield_str)
        bitfield = get_bitfield_spec(start, end)
        tib = "".join(re.split("\[.*\]", tib))
        print(bin(bitfield.mask))


    if re.search(" *^\*", tib):
        # Read or write access tib
        tib = tib[1:]


        if '.' in tib:
            # Using named access
            [reg_str, valmask] = re.split(" *= *", tib)
            regbank_name = sheet_name = register_name = subfield_name = None
            if reg_str.count('.')==3:
                [regbank_name, sheet_name, register_name, subfield_name] = \
                        reg_str.split('.')
            elif reg_str.count('.')==2:
                [regbank_name, sheet_name, register_name] = \
                        reg_str.split('.')
            elif reg_str.count('.')<=1:
                assert 0, "Invalid register read command specified"

            if re.search("\?$", tib):
                # Read register specified
                value = model.read_register(regbank_name, sheet_name, register_name, subfield_name)
                if value==None:
                    # TODO, patch this
                    set_trace()
                    pass
                model.display_read_register(regbank_name, sheet_name, register_name, subfield_name,
                        value)
            elif re.search("\?", tib):
                # Read-modify-write register specified
                value = eval(valmask.replace('?', ''))
                set_trace() # TODO
                pass
            else :
                # Write register specified
                value = eval(valmask)
                model.write_register(regbank_name, sheet_name, register_name, subfield_name, value)
                pass
        else:
            # Using address access
            [addr, valmask] = re.split(" *= *", tib)
            addr = int(addr, 0)
            if re.search("\?$", tib):
                # Read address
                value = self.read_address(addr)
                if value != None:
                    print("* {0} [{1}:{2}] = {3} ".format(hex(addr),
                            bitfield.bitfield_end, bitfield.bitfield_start,
                            hex((value & bitfield.bitfield_mask ) >>
                            bitfield.bitfield_rshift)))
                else:
                    print("* {0} [{1}:{2}]: Read failed ".format(hex(addr),
                            bitfield.bitfield_end, bitfield.bitfield_start))
            elif re.search("\?", valmask):
                # Read modify write
                value = eval(valmask.replace('?', ''))
                read_value = self.read_address(addr)
                write_value = read_value
                if bitfield.bitfield_value:
                    if value > (value & bitfield.bitfield_mask) :
                        print ("Warning : Value specified exceeds the"
                                " bit field specified")
                    write_value |= (value & bitfield.bitfield_mask) << \
                        bitfield.bitfield_rshift
                else:
                    write_value |= value

                if self.write_address(addr, write_value):
                    print("* {0} [{1}:{2}] = {3} : Read-modify-write "
                                "success ".format(hex(addr), bitfield.bitfield_end,
                                bitfield.bitfield_start, hex(write_value)))
                else:
                    print("* {0} [{1}:{2}] = {3} : Read-modify-write "
                            "failed ".format(hex(addr), bitfield.bitfield_end,
                                bitfield.bitfield_start, hex(write_value)))
            else:
                # Write address
                value = eval(valmask)
                write_value = 0
                if bitfield.bitfield_value:
                    if value > (value & bitfield.bitfield_mask) :
                        print ("Warning : Value specified exceeds the"
                                " bit field specified")
                    write_value |= (value & bitfield.bitfield_mask) << bitfield.bitfield_rshift
                else:
                    write_value |= value
                if self.write_address(addr, write_value):
                    print("* {0} [{1}:{2}] = {3} : Write success ".format(hex(addr), 
                            bitfield.bitfield_end, bitfield.bitfield_start, hex(write_value)))
                else:
                    print("* {0} [{1}:{2}] = {3} : Write failed ".format(hex(addr), 
                            bitfield.bitfield_end, bitfield.bitfield_start, hex(write_value)))
        return

    if re.search(" *^load_regbank", tib):
        # Load the regbank into database
        [_, regbank_file] = re.split(" +", tib)
        if re.search("^.", regbank_file):
            regbank_file = tib_file_path + "/" + regbank_file.replace("\"",'')
        print("Loading regbank {0}".format(regbank_file))
        regbank_parser.regbank_load_excel(regbank_file)
        return
    
    if re.search(" *^unload_regbank", tib):
        # Unload the regbank from database
        [ _ , regbank_name] = re.split(" +", tib)
        print("Unloading regbank {0}".format(regbank_name))
        regbank_parser.regbank_unload(regbank_name)
        return

    if re.search("^load_sheet", tib):
        # Load the regbank sheet into database 
        regbank_sheet = base_addr = offset_type = as_sheet = None
        if re.search(" +using +", tib) and re.search(" +as +", tib):
            [ _, regbank_sheet, _, base_addr, _, offset_type, _, as_sheet ] = \
                    re.split(" +", tib)
        elif re.search(" +using +", tib):
            [ _, regbank_sheet, _, base_addr, _, offset_type] = \
                    re.split(" +", tib)
        else :
            [ _, regbank_sheet, _, base_addr,] = \
                    re.split(" +", tib)
        if offset_type==None:
            offset_type = offsets_enum_t.BYTE_OFFSETS
        elif offset_type=="BYTE_OFFSETS":
            offset_type = offsets_enum_t.BYTE_OFFSETS
        elif offset_type=="WORD_OFFSETS":
            offset_type = offsets_enum_t.WORD_OFFSETS
        else:
            assert 0, "Unknown offset type specified"
        
        base_addr = int(base_addr, 0)
        [regbank_name, sheet_name] = regbank_sheet.split('.')

        if as_sheet==None:
            as_sheet = sheet_name

        print("Loading regbank sheet {0} from regbank {1} as {2} at {3}".format(
                sheet_name, regbank_name, as_sheet, hex(base_addr)))
        regbank_parser.regbank_load_sheet(regbank_name, sheet_name, base_addr,
                offset_type, as_sheet)
        # MMAP the sheet space
        assert self.target_connected, "Target must be connected to load regbank sheets"
        sheet = self.db[regbank_name][as_sheet]
        return

    if re.search(" *^unload_sheet", tib):
        # Unload the regbank from database
        [ _ , arg_str] = re.split(" +", tib)
        assert arg_str.count('.')==1, "Unload format unknown"
        [regbank_name, sheet_name] = arg_str.split('.')
        print("Unloading sheet {0} from {1}".format(sheet_name, regbank_name))
        regbank_parser.regbank_unload_sheet(regbank_name, sheet_name)
        return


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

## Exported API
def connect(unique_id, unique_msg):
    model.client.set_server_id(unique_id)
    model.client.set_server_msg(unique_msg)
    while 1:
        msg = model.client.get_udp_message()
        if msg:
            [protocol, ip_addr, port, max_msg_len, server_unique_id, server_unique_msg] = msg;
            server_unique_id = int(server_unique_id, 0)
            target = target_t(ip_addr, port, protocol, max_msg_len, server_unique_id, server_unique_msg)
            break
        else:
            print("No server found, please start the server.")
            os._exit(0)
        
    if model.target_connected:
        model.disconnect_from_target()   
    model.add_new_target(target)
    model.connect_to_target(target)


def load_regbank(regbank_file):
    if re.search("^\.", regbank_file):
        try:
            regbank_file = dirname(model.tib_file) + "/" + regbank_file
        except:
            set_trace()
    record = "load_regbank(\"{0}\")".format(regbank_file)
    model.regbank_load_sequence.append(record)
    regbank_parser.regbank_load_excel(regbank_file)
    model.signal_regbank_file_loaded.emit(regbank_file)

def unload_regbank(name):
    pass

def load_sheet(regbank_sheet, base_addr, offset_size, as_sheet=None):
    offset_type = offsets_enum_t.BYTE_OFFSETS if offset_size==1 else \
        offsets_enum_t.WORD_OFFSETS
    regbank_name = regbank_sheet.__regbank_name__
    sheet_name   = regbank_sheet.__sheet_name__
    record = "load_sheet({0}.{1}, {2}, {3}, {4})".format(regbank_name, sheet_name,
            hex(base_addr), hex(offset_size), as_sheet)
    model.regbank_load_sequence.append(record)
    if not regbank_parser.is_regbank_sheet_loaded(regbank_name, sheet_name, as_sheet):
        regbank_parser.regbank_load_sheet(regbank_name, sheet_name, base_addr,
            offset_type, as_sheet)
        predicted_offset_type = regbank_parser.regbank_offset_size_predict(
                model.db[regbank_name][as_sheet if as_sheet else sheet_name])
        assert predicted_offset_type==offset_type, "Predicted offset type" \
            "different from given offset type"
        model.signal_regbank_updated.emit()



def unload_sheet(regbank_sheet):
    regbank_name = regbank_sheet.__regbank_name__
    sheet_name   = regbank_sheet.__sheet_name__
    regbank_parser.regbank_unload_sheet(regbank_name, sheet_name)
    

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



