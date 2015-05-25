
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <fcntl.h>
#include "utils.h"
#include "msg_parser.h"

#define PAGE_SIZE ((size_t)getpagesize())
#define PAGE_MASK ((long)~(PAGE_SIZE - 1))

msg_req_t temp;

static msg_parser_ctxt_t msg_parser_ctxt;
static msg_parser_ctxt_t *g_msg_parser_ctxt = &msg_parser_ctxt;

static uint8_t * msg_parser_mmap(int fd, msg_address_t start_addr, msg_address_t end_addr)
{
    
    uint8_t * rv = (uint8_t *)mmap((void*)(intptr_t)start_addr, (end_addr-start_addr+1), PROT_READ | PROT_WRITE,
            MAP_SHARED, fd, (off_t) (start_addr & PAGE_MASK));
    if (rv == MAP_FAILED) {
        return NULL;
    } else {
        rv += (uint32_t)(start_addr & ~PAGE_MASK);
        if (!(rv==(uint8_t *)(intptr_t)start_addr)) {
            return NULL;
        }
        return rv;
    }
}

static uint8_t msg_parser_munmap(msg_address_t start_addr, msg_address_t end_addr)
{
    return munmap((void*)(intptr_t)start_addr, (end_addr-start_addr+1));
}

void msg_parser_init()
{
    memset(g_msg_parser_ctxt, 0x00, sizeof(msg_parser_ctxt_t));
    g_msg_parser_ctxt->parser_state = MSG_PARSER_UNINITIALIZED_STATE;
}

static bool msg_parser_mmap_space(msg_address_t start, msg_address_t end)
{
    int mem_fd;
    void * ptr;
    if (g_msg_parser_ctxt->start_addr || g_msg_parser_ctxt->end_addr) {
        msg_parser_munmap(g_msg_parser_ctxt->start_addr, g_msg_parser_ctxt->end_addr);
    }
    g_msg_parser_ctxt->start_addr = start;
    g_msg_parser_ctxt->end_addr   = end;
    mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        perror("open(/dev/mem, O_RDWR | O_SYNC) failed");
        return false;
    }
    ptr = msg_parser_mmap(mem_fd, start, end);
    close(mem_fd);
    if (ptr==NULL) {
        return false;
    } else {
        return true;
    }
}

static bool check_address(msg_address_t addr)
{
    if ((addr > g_msg_parser_ctxt->start_addr) && 
        (addr < g_msg_parser_ctxt->end_addr)) {
        return true;
    } else {
        return false;
    }
}

static void msg_parser_resp(msg_handle_type_t msg_handle,
                     msg_req_type_t msg_req_type, 
                     msg_status_type_t status = STATUS_OK, 
                     msg_address_t msg_addr=0,
                     msg_val_t ret_val = 0)
{
    msg_resp_t *resp;
    assert(g_msg_parser_ctxt->msg_resp_buffer);
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
    switch (val_size) {
        case 1:
            {
                ret_val = *(uint8_t*)(intptr_t)addr;
            }
            break;
        case 2:
            {
                ret_val = *(uint16_t*)(intptr_t)addr;
            }
            break;
        case 4:
            {
                ret_val = *(uint32_t*)(intptr_t)addr;
            }
            break;
        default :
            assert(0);
    }
    return ret_val;
}

static uint32_t write_value(msg_address_t addr, msg_val_t val, uint8_t val_size)
{
    msg_val_t ret_val = -1;
    switch (val_size) {
        case 1:
            {
                *(uint8_t*)(intptr_t)addr = val;
                ret_val = *(uint8_t*)(intptr_t)addr;
            }
            break;
        case 2:
            {
                *(uint16_t*)(intptr_t)addr = val;
                ret_val = *(uint16_t*)(intptr_t)addr;
            }
            break;
        case 4:
            {
                *(uint32_t*)(intptr_t)addr = val;
                ret_val = *(uint32_t*)(intptr_t)addr;
            }
            break;
        default :
            assert(0);
    }
    return ret_val;
}

void msg_parser(char *msg_req_buffer, char *msg_resp_buffer, uint32_t *msg_len)
{
    msg_req_t         * req;
    msg_val_t           ret_msg_val;
    /* Store req and resp buffers into global context to work for current message */
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
    if (req->req_type==MEM_MAP_SPACE_REQ) {
        msg_status_type_t status;
        msg_address_t start_addr, end_addr;
        start_addr = req->start_addr;
        end_addr   = req->end_addr;
        if (msg_parser_mmap_space(start_addr, end_addr)) {
            status = STATUS_OK;
        } else {
            status = STATUS_FAIL;
        }
        msg_parser_resp(req->handle, req->req_type, status);
    } else {
        if (check_address(req->addr)) {
            ret_msg_val = -1;
            switch (req->req_type) {
                case BYTE_READ_REQ:
                        ret_msg_val = read_value(req->addr, 1);   
                        break;
                case BYTE_WRITE_REQ:
                        ret_msg_val = write_value(req->addr, req->value, 1);   
                        break;
                case HALF_WORD_READ_REQ:
                        ret_msg_val = read_value(req->addr, 2);   
                        break;
                case HALF_WORD_WRITE_REQ:
                        ret_msg_val = write_value(req->addr, req->value, 2);   
                        break;
                case WORD_READ_REQ:
                        ret_msg_val = read_value(req->addr, 4);   
                        break;
                case WORD_WRITE_REQ:
                        ret_msg_val = write_value(req->addr, req->value, 4);   
                        break;
                    break;
                default:
                    assert(true);
            }
            msg_parser_resp(req->handle, req->req_type, STATUS_OK,
                    req->addr, ret_msg_val);
        } else {
            msg_parser_resp(req->handle, req->req_type, STATUS_INVALID);
        }
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
