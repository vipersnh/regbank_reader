#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <cstring>
#include <stdint.h>
#include <string>
#include <signal.h>
#include "server.h"


#define UDP_PORT 2222
#define TCP_PORT 3333
#define UDP_REPEAT_TIMEOUT 2
#define TCP_ALIVE_TIMEOUT 100

server svr(UDP_PORT, TCP_PORT, UDP_REPEAT_TIMEOUT, TCP_ALIVE_TIMEOUT);

void ctrl_c_handler(int sig)
{
    svr.stop();
}


int main()
{
    signal(SIGINT, ctrl_c_handler);
    signal(SIGABRT, ctrl_c_handler);
    atexit((void (*)())ctrl_c_handler);
    printf("Starting server \n");
    svr.start((void*)&svr);
}


