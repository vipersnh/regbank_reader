from PyQt4.QtCore import QObject, pyqtSignal, QThread
from collections import namedtuple
from regbank_parser import *
from client import *;

class regbank_db_t:
    def __init__(self, db=None, base_addr=None, offset_size=None):
        self.db = db;
        self.base_addr = base_addr;
        self.offset_size = offset_size;

register_t   = namedtuple("register_t", ["base_addr", "offset_size", "element"]);
register_t.__new__.__defaults__ = (None, None, None);

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
    signal_register_info = pyqtSignal(register_t);
    signal_target_info  = pyqtSignal(list);
    signal_target_connection = pyqtSignal(str);
    signal_regbank_connection = pyqtSignal(str);
    signal_regbank_list = pyqtSignal(int, list);
    signal_error        = pyqtSignal(str);

    target_search_thread = None;

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

    def initialize(self):
        self.signal_target_connection.emit("Waiting for targets");
        self.signal_regbank_connection.emit("Load new regbank");
        self.target_search_thread = QThread();
        self.moveToThread(self.target_search_thread);
        self.target_search_thread.started.connect(self.target_search);
        self.target_search_thread.start();

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

    def connect_to_target(self, target):
        self.selected_target = target;
        self.signal_target_connection.emit("Disconnect");
        self.client.connect_to_server([target.protocol, target.ip_addr, target.port, target.max_msg_len])

    def disconnect_target(self, target):
        self.selected_target = None;
        self.signal_target_connection.emit("Connect");
        self.client.disconnect_server();

    def load_regbank_file(self, fname):
        regbank_db      = regbank_db_t();
        regbank_db.db   = regbank_to_database(fname);
        regbank_db.base_addr = None;
        regbank_db.offset_size = regbank_offset_size_predict(regbank_db.db);
        self.regbank_db_list.append(regbank_db);
        self.signal_regbank_connection.emit("Load another regbank");
        regbanks_list = [];
        for item in self.regbank_db_list:
            regbanks_list.append(item.db.regbank_name);
        self.signal_regbank_list.emit(len(self.regbank_db_list)-1, regbanks_list);

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
            for register in  sheet.elements:
                registernames.append(register.register_name);
            registers_list.append(registernames);
        self.signal_regbank_info.emit(sheetnames, registers_list);
    

    def get_register(self, regbank_idx, sheet_idx, register_idx):
        if self.regbank_db_list[regbank_idx].base_addr==None:
            assert(0);
        base_addr = self.regbank_db_list[regbank_idx].base_addr;
        offset_size = self.regbank_db_list[regbank_idx].offset_size;
        element      = self.regbank_db_list[regbank_idx].db.sheets[sheet_idx].elements[register_idx];
        register = register_t(base_addr, offset_size, element);
        self.signal_register_info.emit(register);

    def update_mmap(self, start_addr, end_addr):
        msg_mmap_init = msg_req_t();
        msg_mmap_init.handle = id(start_addr)+id(end_addr);
        msg_mmap_init.req_type = MEM_MAP_SPACE_REQ;
        msg_mmap_init.start_addr = start_addr;
        msg_mmap_init.end_addr   = end_addr;
        resp = self.client.query_server(msg_mmap_init);
    
    def update_regbank_additional_info(self, regbank_info):
        for idx, val in enumerate(self.regbank_db_list):
            if val.db.regbank_name==regbank_info.regbank_name:
                val.base_addr = regbank_info.base_addr;
                val.offset_size = regbank_info.offset_size;
                break;
        self.get_regbank_sheets_registers(regbank_info.regbank_name);

    def read_register(self, register):
        msg_read = msg_req_t();
        msg_read.handle = id(register);
        msg_read.req_type = WORD_READ_REQ;
        msg_read.addr = register.base_addr+register.offset_size*register.element.offset_addr;
        resp = self.client.query_server(msg_read);

    def write_register(self, register, value):
        msg_write = msg_req_t();
        msg_write.handle = id(register);
        msg_write.req_type = WORD_WRITE_REQ;
        msg_write.addr = register.base_addr+register.offset_size*register.element.offset_addr;
        msg_write.value = value;
        resp = self.client.query_server(msg_read);

