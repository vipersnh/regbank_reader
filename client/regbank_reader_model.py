from PyQt4.QtCore import QObject, pyqtSignal, QThread, QMutex, Qt, qDebug
from PyQt4.QtGui import QMessageBox
from collections import namedtuple
from regbank_parser import *
from client import *;

class regbank_db_t:
    def __init__(self, db=None, base_addr=None, offset_size=None):
        self.db = db;
        self.base_addr = base_addr;
        self.offset_size = offset_size;
        self.start_addr  = None;
        self.end_addr    = None;

class register_t:
    def __init__(self, register_name,  base_addr=None, offset_addr= None, offset_size=None, sub_elements=None):
        self.name = register_name;
        self.base_addr = base_addr;
        self.offset_addr = offset_addr;
        self.offset_size = offset_size;
        self.sub_elements = sub_elements;

regbank_additional_info_t = namedtuple("regbank_additional_info_t", ["regbank_name", "base_addr", "offset_size"]);
regbank_additional_info_t.__new__.__defaults__ = (None, None, None);

#class target_t :
#    def __init__(self, ip_addr=None, port=None, protocol=None):
#        self.ip_addr = ip_addr;
#        self.port = port;
#        self.protocol = protocol;
#    
#    def __eq__(self, other):
#        return ((self.ip_addr==other.ip_addr) and
#                (self.port==other.port) and
#                (self.protocol==other.protocol));

target_t     = namedtuple("target_t", ["ip_addr", "port", "protocol", "max_msg_len"]);

class regbank_reader_model_t(QObject):
    signal_regbank_info = pyqtSignal(list, list);
    signal_target_info  = pyqtSignal(list);
    signal_target_connection = pyqtSignal(str);
    signal_regbank_connection = pyqtSignal(str);
    signal_regbank_list = pyqtSignal(int, list);
    signal_error        = pyqtSignal(str);

    target_search_thread = None;
    keep_alive_thread = None;
    def __init__(self, server_udp_port=2222):
        super(regbank_reader_model_t, self).__init__();
        self.client = client_t(server_udp_port);
        self.selected_target = None;
        self.selected_regbank_db_idx = None;
        # Database to hold all loaded regbanks
        self.regbank_db_list = [];
        # Database to hold all registers being operated upon
        self.registers_list  = [];
        # Database to hold all targets listed
        self.targets_list = [];
        self.target_connected = False;
        self.mmap_done = False;

    def initialize(self):
        self.signal_target_connection.emit("Waiting for targets");
        self.signal_regbank_connection.emit("Load new regbank");
        self.target_search_thread = QThread();
        self.target_search_thread.started.connect(self.target_search, Qt.DirectConnection);
        self.target_search_thread.start();
        self.keep_alive_thread = QThread();
        self.keep_alive_thread.started.connect(self.keep_alive, Qt.DirectConnection);
        self.keep_alive_thread.start();

    def add_new_target(self ,target):
        target_already_listed = False;
        for item  in self.targets_list:
            if target==item:
                target_already_listed = True;
                break;

        if not target_already_listed:
            print("New target found");
            self.targets_list.append(target);
            self.signal_target_info.emit(self.targets_list);
        
        if self.selected_target==None:
            self.signal_target_connection.emit("Connect");
        
    def target_search(self):
        print("Target search thread started");
        while (1):
            [protocol, ip_addr, port, max_msg_len] = self.client.get_udp_message();
            target = target_t(ip_addr, port, protocol, max_msg_len);
            self.add_new_target(target);

    def keep_alive(self):
        print("Keep alive thread started");
        while(1):
            self.keep_alive_thread.sleep(10);
            if self.target_connected:
                msg_write = msg_req_t();
                msg_write.handle = 0xABCDFABC;
                msg_write.req_type = KEEP_ALIVE_REQ;
                msg_write.addr = 0x00;
                msg_write.value = 0x00;
                resp = self.client.query_server(msg_write);

    def connect_to_target(self, target):
        self.target_connected = True;
        self.selected_target = target;
        self.signal_target_connection.emit("Disconnect");
        self.client.connect_to_server([target.protocol, target.ip_addr, target.port, target.max_msg_len])

    def disconnect_target(self, target):
        self.target_connected = False;
        self.mmap_done = False;
        self.selected_target = None;
        self.signal_target_connection.emit("Connect");
        self.client.disconnect_server();

    def slot_regbank_changed(self, regbank_name):
        for idx, rb in enumerate(self.regbank_db_list):
            if rb.db.regbank_name==regbank_name:
                self.selected_regbank_db_idx = idx;

    def load_regbank_file(self, fname):
        regbank_db      = regbank_db_t();
        regbank_db.db   = regbank_to_database(fname);
        regbank_db.base_addr = None;
        regbank_db.offset_size = regbank_offset_size_predict(regbank_db.db);
        self.regbank_db_list.append(regbank_db);
        self.signal_regbank_connection.emit("Load another regbank");

    def get_regbank_sheets_registers(self, regbank_name):
        sheetnames = [];
        registers_list  = [];
        selected_db = None;
        for idx, val in enumerate(self.regbank_db_list) :
            if val.db.regbank_name==regbank_name:
                selected_db = val.db;
                break;
        assert(selected_db!=None);
        for sheet in selected_db.sheets:
            sheetnames.append(sheet.sheet_name);
            registernames = [];
            for element in  sheet.elements:
                registernames.append(element.register_name);
            registers_list.append(registernames);
        self.signal_regbank_info.emit(sheetnames, registers_list);
    

    def update_mmap_addresses(self, regbank_name):
        rb = None;
        for regbank in self.regbank_db_list:
            if regbank.db.regbank_name==regbank_name:
                rb = regbank;
                break;
        if rb:
            start_addr = rb.base_addr;
            last_offset = 0;
            for sheet in rb.db.sheets:
                for element in sheet.elements:
                    if element.offset_addr > last_offset:
                        last_offset = element.offset_addr;
            end_addr   = rb.base_addr + last_offset*rb.offset_size;
            rb.start_addr = start_addr;
            rb.end_addr   = end_addr;
        else:
            assert(0);

    def get_register(self, regbank_idx, sheet_idx, register_idx):
        if self.regbank_db_list[regbank_idx].base_addr==None:
            assert(0);
        base_addr = self.regbank_db_list[regbank_idx].base_addr;
        offset_size = self.regbank_db_list[regbank_idx].offset_size;
        element      = self.regbank_db_list[regbank_idx].db.sheets[sheet_idx].elements[register_idx];
        register = register_t(element.register_name, base_addr, element.offset_addr, offset_size, element.sub_elements);
        return register;

    def update_mmap(self, start_addr, end_addr):
        self.mmap_done = True;
        msg_mmap_init = msg_req_t();
        msg_mmap_init.handle = id(start_addr)+id(end_addr);
        msg_mmap_init.req_type = MEM_MAP_SPACE_REQ;
        msg_mmap_init.start_addr = start_addr;
        msg_mmap_init.end_addr   = end_addr;
        resp = self.client.query_server(msg_mmap_init);
        if resp.status==STATUS_OK:
            self.mmap_done = True
        else:
            print("MMAP Failed on server side!");
    
    def update_regbank_additional_info(self, regbank_info):
        for idx, val in enumerate(self.regbank_db_list):
            if val.db.regbank_name==regbank_info.regbank_name:
                val.base_addr = regbank_info.base_addr;
                val.offset_size = regbank_info.offset_size;
                break;
        self.update_mmap_addresses(regbank_info.regbank_name);
        regbanks_list = [];
        for item in self.regbank_db_list:
            regbanks_list.append(item.db.regbank_name);
        self.selected_regbank_db_idx = len(self.regbank_db_list)-1;
        self.signal_regbank_list.emit(len(self.regbank_db_list)-1, regbanks_list);
        self.get_regbank_sheets_registers(regbank_info.regbank_name);

    def targetInitialized(self):
        if self.target_connected==False:
            msgBox = QMessageBox();
            msgBox.setText("Target not connected, please connect");
            msgBox.exec();
            return False;
        elif self.mmap_done==False:
            rb = self.regbank_db_list[self.selected_regbank_db_idx];
            try:
                self.update_mmap(rb.start_addr, rb.end_addr);
            except:
                set_trace();
                pass;
        return True;

    def read_register(self, register):
        if self.targetInitialized():
            msg_read = msg_req_t();
            msg_read.handle = id(register);
            msg_read.req_type = WORD_READ_REQ;
            msg_read.addr = register.base_addr+register.offset_size*register.offset_addr;
            resp = self.client.query_server(msg_read);
            assert(resp.handle==msg_read.handle);
            if resp.status==STATUS_OK:
                return resp.value; # Read success
            else:
                return None; # Read failed
        else:
            return None; # Read failed

    def write_register(self, register, value):
        if self.targetInitialized():
            msg_write = msg_req_t();
            msg_write.handle = id(register);
            msg_write.req_type = WORD_WRITE_REQ;
            msg_write.addr = register.base_addr+register.offset_size*register.offset_addr;
            msg_write.value = value;
            resp = self.client.query_server(msg_write);
            assert(resp.handle==msg_write.handle);
            if resp.status==STATUS_OK:
                return True; # Write success
            else:
                return False; # Write failed
        else:
            return False; # Write failed
    
