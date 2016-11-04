#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>

#define PAGE_SIZE ((size_t)getpagesize())
#define PAGE_MASK ((long)~(PAGE_SIZE - 1))

static uint8_t * dynamic_mmap(void * addr)
{
    uint8_t * rv;
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    rv = (uint8_t *)mmap(addr, 0x01, PROT_READ | PROT_WRITE,
            MAP_SHARED, mem_fd, (off_t) ((uint32_t)addr & PAGE_MASK));
    if (rv==MAP_FAILED) {
        exit(-1);
    }
    rv += (uint32_t) ( (uint32_t)addr & ~PAGE_MASK);
    return rv;
}


int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Enter an address to read or enter an address and value to write\n");
        exit(-1);
    } else {
        uint32_t address = 0;
        uint32_t value = 0;
        volatile uint32_t * ptr;
        bool is_read = true;
        switch (argc) {
        case 2:
            sscanf(argv[1], "%i", &address);
            is_read = true;
            break;
        case 3:
            sscanf(argv[1], "%i", &address);
            sscanf(argv[2], "%i", &value);
            is_read = false;
            break;
        default:
            printf("Unknown error\n");
            exit(-1);
        }
        
        ptr = (uint32_t*) dynamic_mmap((void*)address);
        if (is_read) {
            printf("Value = 0x%x\n", *ptr);
        } else {
            volatile uint32_t read_value;
            *ptr = value;
            read_value = *ptr;
            printf("Value = 0x%x, Set Value = 0x%x\n", value, read_value);
            printf("Write : %s\n", read_value==value ? "Passed" : "Failed");
        }
    }

}


