extern "C" {
    #include <signal.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <cstring>
    #include <stdint.h>
    #include <stdlib.h>
};
#include <iostream>
#include <string>
#include "server.h"
#include "msg_parser.h"
#include "utils.h"


#define UDP_PORT 2222
#define TCP_PORT 3333
#define UDP_REPEAT_TIMEOUT 2
#define TCP_ALIVE_TIMEOUT 100

server *g_svr;

void ctrl_c_handler(int sig)
{
    g_svr->stop();
}


int main(int argc, char *argv[])
{
    switch(argc) {
        case 2:
        case 3:
            {
                uint32_t address = 0;
                uint32_t value = 0;
                uint32_t * ptr;
                bool is_read = true;
                switch (argc) {
                case 2:
                    sscanf(argv[1], "%i", &address);
                    is_read = false;
                case 3:
                    sscanf(argv[1], "%i", &address);
                    sscanf(argv[2], "%i", &value);
                    is_read = false;
                default:
                    assert(0, ASSERT_FATAL);
                }
    
                #if defined(DEBUG_PRINT)
                    printf("Address : 0x%x, Data : 0x%x", address, value);
                #endif
                
                msg_parser_init();
                ptr = (uint32_t*) msg_parser_dynamic_mmap((void*)address);
                if (is_read) {
                    printf("Value = 0x%x\n", *ptr);
                } else {
                    *ptr = value;
                    printf("Value = 0x%x, Set Value = 0x%x\n", value, *ptr);
                }
            }
            break;

        case 4:
            char itf[100];
            uint64_t unique_id;
            char unique_msg[100];
            sscanf(argv[1], "%100s", itf);
            sscanf(argv[2], "%llx", &unique_id);
            sscanf(argv[3], "%100s", unique_msg);
            g_svr = new server(UDP_PORT, TCP_PORT, UDP_REPEAT_TIMEOUT, TCP_ALIVE_TIMEOUT, itf, unique_id, unique_msg);
            signal(SIGINT, ctrl_c_handler);
            signal(SIGTERM, ctrl_c_handler);
            printf("Starting server \n");
            g_svr->start((void*)g_svr);
            break;

        default:
            printf("Enter an interface [eth0, wlan0 or soon] to attach server, unique_id and unique_msg. Exiting\n");
            exit(-1);
            break;
    }
}


