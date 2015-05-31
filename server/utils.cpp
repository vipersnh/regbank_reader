extern "C" {
    #include <stdio.h>
    #include <stdlib.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <signal.h>
};
#include "utils.h"

void assert_failed(const char *func, int line, assert_criticality_t crt)
{
    pid_t pid = getpid();
    printf("Asserted in %s, at %d \n", func, line);
    if (crt==ASSERT_FATAL) {
        kill(pid, SIGTERM);
    }
}
