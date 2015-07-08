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
    if (argc==1 || argc>2) {
        printf("Enter an interface [eth0, wlan0 or soon] to attach server. Exiting\n");
        exit(-1);
    }
    g_svr = new server(UDP_PORT, TCP_PORT, UDP_REPEAT_TIMEOUT, TCP_ALIVE_TIMEOUT, argv[1]);
    signal(SIGINT, ctrl_c_handler);
    signal(SIGTERM, ctrl_c_handler);
    printf("Starting server \n");
    g_svr->start((void*)g_svr);
}


