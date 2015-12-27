from pdb import set_trace
import threading
from PyQt4.QtCore import QObject, Qt
from PyQt4.QtCore import QMutex
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QThread
from ctypes import *
import socket
import pprint
import time
import atexit
import os

MSG_LEN_FIELD_LEN = 2

(   
    BYTE_READ_REQ,
    BYTE_WRITE_REQ,
    HALF_WORD_READ_REQ,
    HALF_WORD_WRITE_REQ,
    WORD_READ_REQ,
    WORD_WRITE_REQ,
    KEEP_ALIVE_REQ,
) = range(7)

(
    STATUS_OK,
    STATUS_FAIL,
    STATUS_INVALID,
    STATUS_INCONSISTENT
) = range(4)


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

class client_t(QObject):
    # Signals
    signal_disconnected = pyqtSignal()

    def __init__(self, server_udp_port=2222) :
        super(client_t, self).__init__()
        self.previous_udp_message = []
        self.server_udp_port = server_udp_port
        self.server_connected = False
        self.server_socket_handle = None
        self.local_ip         = "0.0.0.0"
        self.server_unique_id = None
        self.server_unique_msg = None
        self.sync_mutex = QMutex()
        if __debug__:
            self._stored_value = 0x00

    def set_server_udp_port(self, server_udp_port):
        self.server_udp_port = server_udp_port

    def set_server_id(self, unique_id):
        self.server_unique_id = unique_id

    def set_server_msg(self, unique_msg):
        self.server_unique_msg = unique_msg
    
    def get_udp_message(self, timeout) :
        sock = socket.socket(socket.AF_INET, 
                             socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((self.local_ip, self.server_udp_port))
        sock.settimeout(timeout)
        ctime = time.time()
        while 1:
            try:
                data, addr = sock.recvfrom(65535)
            except :
                return None
            data = data.decode("utf-8")
            msgs = data.strip().replace(' ', '').split(',')
            vals = []
            for i in msgs :
                vals.append(i.split(':')[1])
            sock.close()
            del sock
            if int(vals[4],0)==self.server_unique_id and vals[5]==self.server_unique_msg:
                if len(self.previous_udp_message):
                    # Check that this message can come from a single IP address 
                    assert vals==self.previous_udp_message

                self.previous_udp_message = vals
                return vals
            elif time.time() >= ctime + timeout:
                return None

    def disconnect(self) :
        if self.server_connected:
            self.server_socket_handle.close()
            self.server_connected = False
            self.signal_disconnected.emit()

    def query_server(self, msg) :
        assert self.server_connected
        self.sync_mutex.lock()
        msg_bytes = bytearray(msg)
        msg_len = c_ushort(len(msg_bytes))
        msg_bytes[:0] = bytes(msg_len)
        self.server_socket_handle.send(msg_bytes)
        resp = self.server_socket_handle.recv(MSG_LEN_FIELD_LEN)
        msg_len = c_ushort.from_buffer(bytearray(resp)).value
        resp = self.server_socket_handle.recv(msg_len)
        resp_struct = msg_resp_t.from_buffer(bytearray(resp))
        self.sync_mutex.unlock()
        return resp_struct
    
    def print_resp(self, resp) :
        if resp.req_type==KEEP_ALIVE_REQ:
            return
        for field_name, field_type in resp._fields_ :
            print(field_name ," : ", getattr(resp, field_name))

    def keep_alive(self):
        print("Keep alive thread started")
        while(self.server_connected):
            msg_write = msg_req_t()
            msg_write.handle = 0xABCDFABC
            msg_write.req_type = KEEP_ALIVE_REQ
            msg_write.addr = 0x00
            msg_write.value = 0x00
            try:
                resp = self.query_server(msg_write)
            except:
                self.disconnect()
            time.sleep(5)
        del self.keep_alive_thread

    def connect(self, unique_id, unique_msg, timeout):
        self.set_server_id(unique_id)
        self.set_server_msg(unique_msg)
        while 1:
            msg = self.get_udp_message(timeout)
            if msg:
                [protocol, ip_addr, port, max_msg_len, server_unique_id, server_unique_msg] = msg
                server_unique_id = int(server_unique_id, 0)
                self.server_socket_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket_handle.connect((ip_addr, int(port)))
                self.server_connected = True
                self.keep_alive_thread = threading.Thread(target=self.keep_alive)
                self.keep_alive_thread.start()
                break
            else:
                print("No server found, please start the server.")
                break

    def read_address(self, address):
        if __debug__:
            return self._stored_value
        msg_read = msg_req_t()
        msg_read.handle = id(address)
        msg_read.req_type = WORD_READ_REQ
        msg_read.addr = address
        try:
            resp = self.query_server(msg_read)
        except:
            self.disconnect()
            return 0
        assert(resp.handle==msg_read.handle)
        if resp.status==STATUS_OK:
            assert resp.value != None, "Invalid state"
            return resp.value # Read success
        else:
            set_trace()
            return None       # Read failed

    def write_address(self, address, value):
        if __debug__:
            self._stored_value = value
            return True
        msg_write = msg_req_t()
        msg_write.handle = id(address)
        msg_write.req_type = WORD_WRITE_REQ
        msg_write.addr = address
        msg_write.value = value
        try:
            resp = self.query_server(msg_write)
        except:
            self.disconnect()
            return False
        assert(resp.handle==msg_write.handle)
        if resp.status==STATUS_OK:
            return True # Write success
        else:
            return False # Write failed

client = client_t()
