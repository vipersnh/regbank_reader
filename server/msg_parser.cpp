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

static uint8_t * msg_parser_mmap(int fd, msg_address_t start_addr, msg_address_t end_addr)
{
    
    uint8_t * rv = (uint8_t *)mmap((void*)(intptr_t)start_addr, (end_addr-start_addr+1), PROT_READ | PROT_WRITE,
            MAP_SHARED, fd, (off_t) (start_addr & PAGE_MASK));
    if (rv == MAP_FAILED) {
        return NULL;
    } else {
        rv += (uint32_t)(start_addr & ~PAGE_MASK);
        assert(rv==(uint8_t *)(intptr_t)start_addr, ASSERT_FATAL);
        return rv;
    }
}

static uint8_t msg_parser_munmap(msg_address_t start_addr, msg_address_t end_addr)
{
    return munmap((void*)(intptr_t)start_addr, (end_addr-start_addr+1));
}

void msg_parser_init()
{
    uint8_t idx;
    memset(g_msg_parser_ctxt, 0x00, sizeof(msg_parser_ctxt_t));
    for (idx=0; idx < MAX_MMAPS_PER_CONNECTION; idx++) {
        g_msg_parser_ctxt->parser_state[idx] = MSG_PARSER_UNINITIALIZED_STATE;
    }
}

static bool msg_parser_mmap_space(msg_address_t start, msg_address_t end)
{
    int mem_fd;
#if 0
    g_msg_parser_ctxt->start_addr = start;
    g_msg_parser_ctxt->end_addr   = end;
    g_msg_parser_ctxt->parser_state = MSG_PARSER_INITIALIZED_STATE;
    return true;
#endif
    g_msg_parser_ctxt->start_addr[g_msg_parser_ctxt->num_mmaps] = start;
    g_msg_parser_ctxt->end_addr[g_msg_parser_ctxt->num_mmaps]   = end;
    mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        perror("open(/dev/mem, O_RDWR | O_SYNC) failed");
        assert(0, ASSERT_NONFATAL);
        g_msg_parser_ctxt->parser_state[g_msg_parser_ctxt->num_mmaps] = MSG_PARSER_UNINITIALIZED_STATE;
        return false;
    }
    msg_parser_mmap(mem_fd, start, end);
    close(mem_fd);
    g_msg_parser_ctxt->parser_state[g_msg_parser_ctxt->num_mmaps] = 
        MSG_PARSER_INITIALIZED_STATE;
    g_msg_parser_ctxt->num_mmaps++;
    assert(g_msg_parser_ctxt->num_mmaps <= MAX_MMAPS_PER_CONNECTION, ASSERT_FATAL);
    return true;
}

static bool check_address(msg_address_t addr)
{
    uint8_t idx;
    for (idx=0; idx < g_msg_parser_ctxt->num_mmaps; idx++) {
        if (g_msg_parser_ctxt->parser_state[idx]==MSG_PARSER_INITIALIZED_STATE) {
            if ((addr >= g_msg_parser_ctxt->start_addr[idx]) && 
                (addr <= g_msg_parser_ctxt->end_addr[idx])) {
                return true;
            } else {
                return false;
            }
        } else {
            return false;
        }
    }
    return false;
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
#if 1
    return 0xABCDEFA;
#endif
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
            assert(0, ASSERT_FATAL);
    }
    return ret_val;
}

void write_value(msg_address_t addr, msg_val_t val, uint8_t val_size)
{
    switch (val_size) {
        case 1:
            {
                *(uint8_t*)(intptr_t)addr = val;
            }
            break;
        case 2:
            {
                *(uint16_t*)(intptr_t)addr = val;
            }
            break;
        case 4:
            {
                *(uint32_t*)(intptr_t)addr = val;
            }
            break;
        default :
            assert(0, ASSERT_FATAL);
    }
}

void msg_parser_munmap_all(void)
{
    int mem_fd;
    uint8_t &num_mmaps = g_msg_parser_ctxt->num_mmaps;
    mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        perror("open(/dev/mem, O_RDWR | O_SYNC) failed");
        assert(0, ASSERT_NONFATAL);
        return ;
    }
    while (num_mmaps) {
        if (g_msg_parser_ctxt->parser_state[num_mmaps-1]==
                MSG_PARSER_INITIALIZED_STATE) {
            msg_parser_mmap(mem_fd,
                    g_msg_parser_ctxt->start_addr[num_mmaps-1],
                    g_msg_parser_ctxt->end_addr[num_mmaps-1]);
            g_msg_parser_ctxt->parser_state[num_mmaps-1]=
                MSG_PARSER_UNINITIALIZED_STATE;
            g_msg_parser_ctxt->start_addr[num_mmaps-1] = 0x00;
            g_msg_parser_ctxt->end_addr[num_mmaps-1] = 0x00;
        } else {
            assert(0, ASSERT_FATAL); /* Invalid state */
        }
        num_mmaps--;
    }
    close(mem_fd);
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
    if (req->req_type==KEEP_ALIVE_REQ) {
        msg_parser_resp(req->handle, req->req_type, STATUS_OK);
    } else if (req->req_type==MEM_MAP_SPACE_REQ) {
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
