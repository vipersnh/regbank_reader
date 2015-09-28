extern "C" {
    #include <stdio.h>
    #include <stdint.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <fcntl.h>
};
#include "utils.h"
#include "msg_parser.h"

#define PAGE_SIZE ((size_t)getpagesize())
#define PAGE_MASK ((long)~(PAGE_SIZE - 1))

msg_req_t temp;

static msg_parser_ctxt_t msg_parser_ctxt;
static msg_parser_ctxt_t *g_msg_parser_ctxt = &msg_parser_ctxt;

static uint8_t * msg_parser_dynamic_mmap(void * addr)
{
    uint8_t * rv;
    rv = (uint8_t *)mmap(addr, 0x01, PROT_READ | PROT_WRITE,
            MAP_SHARED, g_msg_parser_ctxt->mem_fd, (off_t) ((uint32_t)addr & PAGE_MASK));
    if (rv==MAP_FAILED) {
        assert(0, ASSERT_FATAL);
    }
    rv += (uint32_t) ( (uint32_t)addr & ~PAGE_MASK);
    return rv;
}

static uint8_t msg_parser_dynamic_munmap(void * addr)
{
    return munmap((void*)((uint32_t)addr & ~PAGE_MASK), 0x01);
}

void msg_parser_init()
{
    memset(g_msg_parser_ctxt, 0x00, sizeof(msg_parser_ctxt_t));
    #if PLATFORM != HOST
        g_msg_parser_ctxt->mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
        if (g_msg_parser_ctxt->mem_fd < 0) {
            perror("open(/dev/mem, O_RDWR | O_SYNC) failed");
            assert(0, ASSERT_NONFATAL);
        }
    #endif
}

static void msg_parser_resp(msg_handle_type_t msg_handle,
                     msg_req_type_t msg_req_type, 
                     msg_status_type_t status = STATUS_OK, 
                     msg_address_t msg_addr=0,
                     msg_val_t ret_val = 0)
{
    msg_resp_t *resp;
    assert(g_msg_parser_ctxt->msg_resp_buffer, ASSERT_FATAL);
    resp = (msg_resp_t *) g_msg_parser_ctxt->msg_resp_buffer;
    resp->handle = msg_handle;
    resp->req_type = msg_req_type;
    resp->status   = status;
    resp->addr = msg_addr;
    resp->value = ret_val;
    *(g_msg_parser_ctxt->msg_len) = sizeof(msg_resp_t);
}

static msg_val_t read_value(msg_address_t addr, uint8_t val_size)
{
    msg_val_t ret_val = -1;
#if PLATFORM == HOST
    return 0xABCDEFA;
#endif
    msg_address_t mapped_addr = (msg_address_t)msg_parser_dynamic_mmap((void*)addr);
    switch (val_size) {
        case 1:
            {
                ret_val = *(uint8_t*)(intptr_t)mapped_addr;
            }
            break;
        case 2:
            {
                ret_val = *(uint16_t*)(intptr_t)mapped_addr;
            }
            break;
        case 4:
            {
                ret_val = *(uint32_t*)(intptr_t)mapped_addr;
            }
            break;
        default :
            assert(0, ASSERT_FATAL);
    }
    msg_parser_dynamic_munmap((void*)mapped_addr);
    return ret_val;
}

void write_value(msg_address_t addr, msg_val_t val, uint8_t val_size)
{
#if PLATFORM == HOST
    return;
#endif
    msg_address_t mapped_addr = (msg_address_t)msg_parser_dynamic_mmap((void*)addr);
    switch (val_size) {
        case 1:
            {
                *(uint8_t*)(intptr_t)mapped_addr = val;
            }
            break;
        case 2:
            {
                *(uint16_t*)(intptr_t)mapped_addr = val;
            }
            break;
        case 4:
            {
                *(uint32_t*)(intptr_t)mapped_addr = val;
            }
            break;
        default :
            assert(0, ASSERT_FATAL);
    }
    msg_parser_dynamic_munmap((void*)mapped_addr);
}

void msg_parser(char *msg_req_buffer, char *msg_resp_buffer, uint32_t *msg_len)
{
    msg_req_t         * req;
    msg_val_t           ret_msg_val;
    /* Store req and resp buffers into global context
     * to work for current message */
    g_msg_parser_ctxt->msg_req_buffer   = msg_req_buffer;
    g_msg_parser_ctxt->msg_resp_buffer  = msg_resp_buffer;
    g_msg_parser_ctxt->msg_len          = msg_len;
#if 0
    {
        uint16_t i;
        printf("Bytes : ");
        for (i=0; i<sizeof(msg_req_t); i++) {
            printf("%x ,", (uint8_t)msg_req_buffer[i]);
        }
        printf("\n");
    }
#endif
    req = (msg_req_t *) msg_req_buffer;
    if (req->req_type==KEEP_ALIVE_REQ) {
        msg_parser_resp(req->handle, req->req_type, STATUS_OK);
    } else {
        ret_msg_val = -1;
        switch (req->req_type) {
            case BYTE_READ_REQ:
                    ret_msg_val = read_value(req->addr, 1);   
                    break;
            case BYTE_WRITE_REQ:
                    write_value(req->addr, req->value, 1);   
                    break;
            case HALF_WORD_READ_REQ:
                    ret_msg_val = read_value(req->addr, 2);   
                    break;
            case HALF_WORD_WRITE_REQ:
                    write_value(req->addr, req->value, 2);   
                    break;
            case WORD_READ_REQ:
                    ret_msg_val = read_value(req->addr, 4);   
                    break;
            case WORD_WRITE_REQ:
                    write_value(req->addr, req->value, 4);   
                    break;
            default:
                assert(0, ASSERT_FATAL);
        }
        msg_parser_resp(req->handle, req->req_type, STATUS_OK,
                req->addr, ret_msg_val);
    }
#if 1
    {
        uint16_t i;
        printf("Bytes : ");
        for (i=0; i<sizeof(msg_resp_t); i++) {
            printf("%x ,", (uint8_t)msg_resp_buffer[i]);
        }
        printf("\n");
    }
#endif
}
