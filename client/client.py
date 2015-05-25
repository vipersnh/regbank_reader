from pdb import set_trace
from ctypes import *
import socket;
import pprint;
import time;

MSG_LEN_FIELD_LEN = 2;

(BYTE_READ_REQ,
BYTE_WRITE_REQ,
HALF_WORD_READ_REQ,
HALF_WORD_WRITE_REQ,
WORD_READ_REQ,
WORD_WRITE_REQ,
MEM_MAP_SPACE_REQ) = range(7);

(STATUS_OK,
STATUS_FAIL,
STATUS_INVALID,
STATUS_INCONSISTENT) = range(4);


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
class client_c:
    def __init__(self, server_udp_port) :
        self.server_udp_port = server_udp_port;
        self.server_connected = False;
        self.server_socket_handle = None;
        self.local_ip         = "0.0.0.0";
    
    def get_udp_message(self) :
        assert self.server_connected==False, "Server already connected";
        sock = socket.socket(socket.AF_INET, 
                             socket.SOCK_DGRAM);
        sock.bind((self.local_ip, self.server_udp_port));
        data, addr = sock.recvfrom(65535);
        data = data.decode("utf-8");
        msgs = data.strip().replace(' ', '').split(',');
        print("UDP Message : "+data);
        vals = [];
        for i in msgs :
            vals.append(i.split(':')[1]);
        return vals;

    def connect_to_server(self) :
        [protocol, ip_addr, port, max_msg_len] = self.get_udp_message();
        self.server_socket_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.server_socket_handle.connect((ip_addr, int(port)));
        return [protocol, ip_addr, port, max_msg_len];

    def disconnect_server(self) :
        self.server_socket_handle.close();

    def query_server(self, msg) :
        msg_bytes = bytearray(msg);
        msg_len = c_ushort(len(msg_bytes));
        msg_bytes[:0] = bytes(msg_len);
        self.server_socket_handle.send(msg_bytes);
        resp = self.server_socket_handle.recv(MSG_LEN_FIELD_LEN);
        msg_len = c_ushort.from_buffer(bytearray(resp)).value;
        resp = self.server_socket_handle.recv(msg_len);
        resp_struct = msg_resp_t.from_buffer(bytearray(resp));
#        self.print_resp(resp_struct);
        return resp_struct;
    
    def print_resp(self, resp) :
        for field_name, field_type in resp._fields_ :
            print(field_name ," : ", getattr(resp, field_name));

msg_mmap_init = msg_req_t();
msg_mmap_init.handle = 0xFFAABB;
msg_mmap_init.req_type = MEM_MAP_SPACE_REQ;
msg_mmap_init.start_addr = 0x30000000;
msg_mmap_init.end_addr   = 0x50000000;

msg_dl_sfnsf_write = msg_req_t();
msg_dl_sfnsf_write.handle = 0xFFAABB;
msg_dl_sfnsf_write.req_type = WORD_WRITE_REQ;
msg_dl_sfnsf_write.addr = 0x38500000;
msg_dl_sfnsf_write.value = 0xFF;

msg_dl_sfnsf_read = msg_req_t();
msg_dl_sfnsf_read.handle = 0xFFAABB;
msg_dl_sfnsf_read.req_type = WORD_READ_REQ;
msg_dl_sfnsf_read.addr = 0x38500000;

if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4);
    client = client_c(2222);
    client.connect_to_server();
    resp = client.query_server(msg_mmap_init);
    for i in range(0,10000) :
        resp = client.query_server(msg_dl_sfnsf_read);
    print("Done");
    client.disconnect_server();
