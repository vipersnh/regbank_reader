from pdb import set_trace
from PyQt4.QtCore import QMutex
from ctypes import *
import socket;
import pprint;
import time;
import atexit;

MSG_LEN_FIELD_LEN = 2;

(   
    BYTE_READ_REQ,
    BYTE_WRITE_REQ,
    HALF_WORD_READ_REQ,
    HALF_WORD_WRITE_REQ,
    WORD_READ_REQ,
    WORD_WRITE_REQ,
    KEEP_ALIVE_REQ,
) = range(7);

(
    STATUS_OK,
    STATUS_FAIL,
    STATUS_INVALID,
    STATUS_INCONSISTENT
) = range(4);


class msg_resp_t (Structure) :
    _fields_ = [("handle",      c_uint),
                ("req_type",    c_uint),
                ("status",      c_uint),
                ("addr",        c_uint),
                ("value",       c_uint)]

class type_union (Union) :
    _anonymous_ = ("type1", "type2")
    _fields_ = [("type1", type("typeA", (Structure,), dict(_fields_=[("addr", c_uint), ("value", c_uint)]))),
                ("type2", type("typeB", (Structure,), dict(_fields_=[("start_addr", c_uint), ("end_addr", c_uint)])))]

class msg_req_t (Structure)  :
    _anonymous_ = ("msg",)
    _fields_ = [("handle",      c_uint),
                ("req_type",    c_uint),
                ("msg",         type_union)]

temp = msg_req_t();
class client_t:
    def __init__(self, server_udp_port) :
        self.previous_udp_message = []
        self.server_udp_port = server_udp_port;
        self.server_connected = False;
        self.server_socket_handle = None;
        self.local_ip         = "0.0.0.0";
        self.server_unique_id = None;
        self.server_unique_msg = None;
        self.sync_mutex = QMutex();

    def set_server_id(self, unique_id):
        self.server_unique_id = unique_id

    def set_server_msg(self, unique_msg):
        self.server_unique_msg = unique_msg
    
    def get_udp_message(self, timeout=10) :
        sock = socket.socket(socket.AF_INET, 
                             socket.SOCK_DGRAM);
        sock.bind((self.local_ip, self.server_udp_port));
        sock.settimeout(timeout)
        ctime = time.time()
        while 1:
            try:
                data, addr = sock.recvfrom(65535);
            except :
                return None
            data = data.decode("utf-8");
            msgs = data.strip().replace(' ', '').split(',');
            vals = [];
            for i in msgs :
                vals.append(i.split(':')[1]);
            sock.close()
            del sock
            if int(vals[4],0)==self.server_unique_id and vals[5]==self.server_unique_msg:
                if len(self.previous_udp_message):
                    # Check that this message can come from a single IP address 
                    assert vals==self.previous_udp_message

                self.previous_udp_message = vals
                return vals;
            elif time.time() >= ctime + timeout:
                return None
                

    def connect_to_server(self, target) :
        [protocol, ip_addr, port, max_msg_len] = target;
        self.server_socket_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_socket_handle.connect((ip_addr, int(port)));
        self.server_connected = True;
        return [protocol, ip_addr, port, max_msg_len];

    def disconnect_server(self) :
        if self.server_connected:
            self.server_socket_handle.close();

    def query_server(self, msg) :
        self.sync_mutex.lock();
        msg_bytes = bytearray(msg);
        msg_len = c_ushort(len(msg_bytes));
        msg_bytes[:0] = bytes(msg_len);
        self.server_socket_handle.send(msg_bytes);
        resp = self.server_socket_handle.recv(MSG_LEN_FIELD_LEN);
        msg_len = c_ushort.from_buffer(bytearray(resp)).value;
        resp = self.server_socket_handle.recv(msg_len);
        resp_struct = msg_resp_t.from_buffer(bytearray(resp));
#        self.print_resp(resp_struct);
        self.sync_mutex.unlock();
        return resp_struct;
    
    def print_resp(self, resp) :
        if resp.req_type==KEEP_ALIVE_REQ:
            return;
        for field_name, field_type in resp._fields_ :
            print(field_name ," : ", getattr(resp, field_name));

