from PyQt4.QtCore import QObject, pyqtSignal, QThread, QMutex, Qt, qDebug
from PyQt4.QtGui import QMessageBox
from collections import namedtuple
from regbank_parser import offsets_enum_t
import regbank_parser
from client import *
from os.path import dirname
from sys import exit
from StructDict import StructDict
import re
import types

target_t     = namedtuple("target_t", ["ip_addr", "port", "protocol",
                                       "max_msg_len"])
bitfield_t   = StructDict("bitfield_t", ["value", "mask", 
                                         "rshift", "end",
                                         "start"])

model = ""

#class regbank_reader_model_t(QObject):
#    signal_targets_info  = pyqtSignal(list)
#    signal_target_connection_status = pyqtSignal(str)
#    signal_error        = pyqtSignal(str)
#
#    target_search_thread = None
#    keep_alive_thread = None
#
#    def __init__(self, server_udp_port=2222):
#        super(regbank_reader_model_t, self).__init__()
#        self.client = client_t(server_udp_port)
#        self.selected_target = None
#        # Database to hold all registers being operated upon
#        self.registers_list  = []
#        # Database to hold all targets listed
#        self.targets_list = []
#        self.target_connected = False
#        self.mmap_done = False
#
#    def initialize(self):
#        self.signal_target_connection.emit("Waiting for targets")
#        self.signal_regbank_connection.emit("Load new regbank")
#        self.target_search_thread = QThread()
#        self.target_search_thread.started.connect(self.target_search, 
#                Qt.DirectConnection)
#        self.target_search_thread.start()
#        self.keep_alive_thread = QThread()
#        self.keep_alive_thread.started.connect(self.keep_alive, 
#                Qt.DirectConnection)
#        self.keep_alive_thread.start()
#
#    def add_new_target(self ,target):
#        target_already_listed = False
#        for item  in self.targets_list:
#            if target==item:
#                target_already_listed = True
#                break
#
#        if not target_already_listed:
#            print("New target found")
#            self.targets_list.append(target)
#            self.signal_target_info.emit(self.targets_list)
#        
#        if self.selected_target==None:
#            self.signal_target_connection.emit("Connect")
#        
#    def target_search(self):
#        print("Target search thread started")
#        while (1):
#            [protocol, ip_addr, port, max_msg_len] = 
#                    self.client.get_udp_message()
#            target = target_t(ip_addr, port, protocol, max_msg_len)
#            self.add_new_target(target)
#
#    def keep_alive(self):
#        print("Keep alive thread started")
#        while(1):
#            self.keep_alive_thread.sleep(10)
#            if self.target_connected:
#                msg_write = msg_req_t()
#                msg_write.handle = 0xABCDFABC
#                msg_write.req_type = KEEP_ALIVE_REQ
#                msg_write.addr = 0x00
#                msg_write.value = 0x00
#                resp = self.client.query_server(msg_write)
#
#    def connect_to_target(self, target):
#        self.target_connected = True
#        self.selected_target = target
#        self.signal_target_connection.emit("Disconnect")
#        self.client.connect_to_server([target.protocol, target.ip_addr, 
#                target.port, target.max_msg_len])
#
#    def disconnect_target(self, target):
#        self.target_connected = False
#        self.mmap_done = False
#        self.selected_target = None
#        self.signal_target_connection.emit("Connect")
#        self.client.disconnect_server()
#
#    def slot_regbank_changed(self, regbank_name):
#        for idx, rb in enumerate(self.regbank_db_list):
#            if rb.db.regbank_name==regbank_name:
#                self.selected_regbank_db_idx = idx
#
#    def load_regbank_file(self, fname):
#        regbank_db      = regbank_db_t()
#        regbank_db.db   = regbank_to_database(fname)
#        regbank_db.base_addr = None
#        regbank_db.offset_size = regbank_offset_size_predict(regbank_db.db)
#        self.regbank_db_list.append(regbank_db)
#        self.signal_regbank_connection.emit("Load another regbank")
#
#    def get_regbank_sheets_registers(self, regbank_name):
#        sheetnames = []
#        registers_list  = []
#        selected_db = None
#        for idx, val in enumerate(self.regbank_db_list) :
#            if val.db.regbank_name==regbank_name:
#                selected_db = val.db
#                break
#        assert(selected_db!=None)
#        for sheet in selected_db.sheets:
#            sheetnames.append(sheet.sheet_name)
#            registernames = []
#            for element in  sheet.elements:
#                registernames.append(element.register_name)
#            registers_list.append(registernames)
#        self.signal_regbank_info.emit(sheetnames, registers_list)
#    
#
#    def update_mmap_addresses(self, regbank_name):
#        rb = None
#        for regbank in self.regbank_db_list:
#            if regbank.db.regbank_name==regbank_name:
#                rb = regbank
#                break
#        if rb:
#            start_addr = rb.base_addr
#            last_offset = 0
#            for sheet in rb.db.sheets:
#                for element in sheet.elements:
#                    if element.offset_addr > last_offset:
#                        last_offset = element.offset_addr
#            end_addr   = rb.base_addr + last_offset*rb.offset_size
#            rb.start_addr = start_addr
#            rb.end_addr   = end_addr
#        else:
#            assert(0)
#
#    
#    def update_regbank_additional_info(self, regbank_info):
#        for idx, val in enumerate(self.regbank_db_list):
#            if val.db.regbank_name==regbank_info.regbank_name:
#                val.base_addr = regbank_info.base_addr
#                val.offset_size = regbank_info.offset_size
#                break
#        self.update_mmap_addresses(regbank_info.regbank_name)
#        regbanks_list = []
#        for item in self.regbank_db_list:
#            regbanks_list.append(item.db.regbank_name)
#        self.selected_regbank_db_idx = len(self.regbank_db_list)-1
#        self.signal_regbank_list.emit(len(self.regbank_db_list)-1, regbanks_list)
#        self.get_regbank_sheets_registers(regbank_info.regbank_name)
#
#    def targetInitialized(self):
#        if self.target_connected==False:
#            msgBox = QMessageBox()
#            msgBox.setText("Target not connected, please connect")
#            msgBox.exec()
#            return False
#        elif self.mmap_done==False:
#            rb = self.regbank_db_list[self.selected_regbank_db_idx]
#            try:
#                self.update_mmap(rb.start_addr, rb.end_addr)
#            except:
#                set_trace()
#                pass
#        return True
#
#    def read_register(self, register):
#        if self.targetInitialized():
#            msg_read = msg_req_t()
#            msg_read.handle = id(register)
#            msg_read.req_type = WORD_READ_REQ
#            msg_read.addr = register.base_addr+register.offset_size*register.offset_addr
#            resp = self.client.query_server(msg_read)
#            assert(resp.handle==msg_read.handle)
#            if resp.status==STATUS_OK:
#                return resp.value; # Read success
#            else:
#                return None; # Read failed
#        else:
#            return None; # Read failed
#
#    def write_register(self, register, value):
#        if self.targetInitialized():
#            msg_write = msg_req_t()
#            msg_write.handle = id(register)
#            msg_write.req_type = WORD_WRITE_REQ
#            msg_write.addr = register.base_addr+register.offset_size*register.offset_addr
#            msg_write.value = value
#            resp = self.client.query_server(msg_write)
#            assert(resp.handle==msg_write.handle)
#            if resp.status==STATUS_OK:
#                return True; # Write success
#            else:
#                return False; # Write failed
#        else:
#            return False; # Write failed


class regbank_reader_model_t (QObject):
    # Signals
    signal_targets_list_updated = pyqtSignal(list)
    signal_target_connected = pyqtSignal(target_t)
    signal_target_disconnected = pyqtSignal(target_t)
    signal_tib_file_loaded = pyqtSignal(str)
    signal_regbank_file_loaded = pyqtSignal(str)

    target_search_thread = None
    keep_alive_thread = None

    def __init__(self, tib_file, cmd_line=False, server_udp_port=2222):
        super(regbank_reader_model_t, self).__init__()
        self.db = regbank_parser.db # Reference to actual database
        self.client = client_t(server_udp_port)
        self.targets_list = []
        self.target_connected = False
        self.cmd_line = cmd_line
        self.tib_file = tib_file

    def initialize(self):
        self.target_search_thread = QThread()
        self.target_search_thread.started.connect(self.target_search, 
                Qt.DirectConnection)
        self.target_search_thread.start()
        self.keep_alive_thread = QThread()
        self.keep_alive_thread.started.connect(self.keep_alive, 
                Qt.DirectConnection)
        self.keep_alive_thread.start()

    def add_new_target(self ,target):
        target_already_listed = False
        for item  in self.targets_list:
            if target==item:
                target_already_listed = True
                break

        if not target_already_listed:
            self.targets_list.append(target)
        
        self.signal_targets_list_updated.emit(self.targets_list)
        
    def target_search(self):
        print("Target search thread started")
        while (1):
            [protocol, ip_addr, port, max_msg_len] = \
                    self.client.get_udp_message()
            target = target_t(ip_addr, port, protocol, max_msg_len)
            self.add_new_target(target)

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

    def connect_to_target(self, target):
        self.target_connected = True
        self.selected_target = target
        self.client.connect_to_server([target.protocol, target.ip_addr, 
                target.port, target.max_msg_len])
        self.signal_target_connected.emit(target)

    def disconnect_from_target(self, target):
        self.target_connected = False
        self.selected_target = None
        self.client.disconnect_server()
        self.signal_target_disconnected.emit(target)

    def create_mem_map(self, start_addr, end_addr):
        msg_mmap_init = msg_req_t()
        msg_mmap_init.handle = id(start_addr)+id(end_addr)
        msg_mmap_init.req_type = MEM_MAP_SPACE_REQ
        msg_mmap_init.start_addr = start_addr
        msg_mmap_init.end_addr   = end_addr
        resp = self.client.query_server(msg_mmap_init)
        if resp.status==STATUS_OK:
            return True
        else:
            return False
        


    def read_address(self, address, dynamic_mmap=True):
        if __debug__:
            return 0xABCDEFAB
        msg_read = msg_req_t()
        msg_read.handle = id(address)
        if dynamic_mmap:
            msg_read.req_type = WORD_READ_REQ_UNMAPPED
        else:
            msg_read.req_type = WORD_READ_REQ
        msg_read.addr = address
        resp = self.client.query_server(msg_read)
        assert(resp.handle==msg_read.handle)
        if resp.status==STATUS_OK:
            assert resp.value != None, "Invalid state"
            return resp.value; # Read success
        else:
            return None;       # Read failed

    def write_address(self, address, value, dynamic_mmap=True):
        if __debug__:
            return True
        msg_write = msg_req_t()
        msg_write.handle = id(address)
        if dynamic_mmap:
            msg_write.req_type = WORD_WRITE_REQ_UNMAPPED
        else:
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
            read_value = self.read_address(addr, dynamic_mmap=False)
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
            if subfield_name:
                subfield = register.subfields[subfield_name]
                bitfield = get_bitfield_spec(subfield.bit_position[0], subfield.bit_position[-1])
                read_value = model.read_register(regbank_name, sheet_name, register_name, subfield_name)
                read_value &= bitfield.mask
                assert (write_value <= bitfield.value), "Number given is larger than bitfield specification"
                write_value = read_value | (write_value << bitfield.rshift)
            self.write_address(addr, write_value, dynamic_mmap=False)
        except:
            set_trace()
            pass

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
        success = self.create_mem_map(sheet.start_addr, sheet.end_addr)
        if not success:
            assert 0, "MMAP failed on server side"
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
    tib_file_path = dirname(tib_file)
    if not model.target_connected and not model.cmd_line:
        assert 0, "Target must be connected before parsing tib file"
#    for tib in f:
#        eval(tib, globals(), locals())
#    exec(open(tib_file, "r").read(), globals(), locals())
    global_env = dict()
    for (key, value) in globals().items():
        if type(value)==types.FunctionType:
            global_env[key] = value
    with open(tib_file, "r") as f:
        for tib in f:
            tib = tib.strip()
            if tib=='':
                # Ignore blank line
                continue
            if re.search("^\#", tib):
                # Ignore tib as it is a comment
                continue

            if '#' in tib:
                # Trim contents after '#' in the tib
                tib = tib[:tib.find('#')].strip()

            for (key, value) in regbank_parser.db_dict.items():
                if key not in global_env.keys():
                    global_env[key] = value
            exec(tib, global_env)
    model.signal_tib_file_loaded.emit(tib_file)        

def initialize():
    pass

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
    model = regbank_reader_model_t(fnames[0], cmd_line)
    from script_api import *
    if cmd_line:
        parse_tib_file(fnames[0])
