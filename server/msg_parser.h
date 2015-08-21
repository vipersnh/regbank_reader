#ifndef _MSG_PARSER_H_

#define DATA_TYPE uint32_t

typedef DATA_TYPE msg_handle_type_t;
typedef DATA_TYPE msg_req_type_t;  
typedef DATA_TYPE msg_status_type_t;
typedef DATA_TYPE msg_address_t;  
typedef DATA_TYPE msg_val_t;	  

#define MSG_HANDLE_TYPE_SIZE    sizeof(DATA_TYPE)
#define MSG_REQ_TYPE_SIZE 	    sizeof(DATA_TYPE)
#define MSG_ADDR_TYPE_SIZE 	    sizeof(DATA_TYPE)
#define MSG_VAL_TYPE_SIZE  	    sizeof(DATA_TYPE)

/* msg_req_type_enum formats
 * BYTE_READ_REQ            : handle = {32 bit random handle}, 
 *                            type   = {BYTE_READ_REQ}, 
 *                            val    = {address}
 * BYTE_WRITE_REQ           : handle = {32 bit random handle}, 
 *                            type   = {BYTE_WRITE_REQ}, 
 *                            val    = {address, val}
 * HALF_WORD_READ_REQ       : handle = {32 bit random handle}, 
 *                            type   = {HALF_WORD_READ_REQ}, 
 *                            val    = {address}
 * HALF_WORD_WRITE_REQ      : handle = {32 bit random handle}, 
 *                            type   = {HALF_WORD_WRITE_REQ}, 
 *                            val    = {address, val}
 * WORD_READ_REQ            : handle = {32 bit random handle}, 
 *                            type   = {WORD_READ_REQ}, 
 *                            val    = {address}
 * WORD_WRITE_REQ           : handle = {32 bit random handle}, 
 *                            type   = {WORD_WRITE_REQ}, 
 *                            val    = {address, val}
 * KEEP_ALIVE_REQ           : handle = {32 bit random handle}, 
 *                            type   = {KEEP_ALIVE_REQ}
 */

typedef enum {
    BYTE_READ_REQ,
    BYTE_WRITE_REQ,
    HALF_WORD_READ_REQ,
    HALF_WORD_WRITE_REQ,
    WORD_READ_REQ,
    WORD_WRITE_REQ,
    KEEP_ALIVE_REQ,
} msg_req_type_enum;

typedef enum {
    STATUS_OK,
    STATUS_FAIL,
    STATUS_INVALID,
    STATUS_INCONSISTENT,
} msg_resp_status_enum;

/* Msg response formats
 * BYTE_READ_REQ        : handle = {32 bit handle from req}, req_type = {BYTE_READ_REQ}, status = {status}, val = {address, value}
 * BYTE_WRITE_REQ       : handle = {32 bit handle from req}, req_type = {BYTE_WRITE_REQ}, status = {status}, val = {address, value}
 * HALF_WORD_READ_REQ   : handle = {32 bit handle from req}, req_type = {HALF_WORD_READ_REQ}, status = {status}, val = {address, value}
 * HALF_WORD_WRITE_REQ  : handle = {32 bit handle from req}, req_type = {HALF_WORD_WRITE_REQ}, status = {status}, val = {address, value}
 * WORD_READ_REQ        : handle = {32 bit handle from req}, req_type = {WORD_READ_REQ}, status = {status}, val = {address, value}
 * WORD_WRITE_REQ       : handle = {32 bit handle from req}, req_type = {WORD_WRITE_REQ}, status = {status}, val = {address, value}
 * KEEP_ALIVE_REQ       : handle = {32 bit handle from req}, req_type = {KEEP_ALIVE_REQ}, status = {STATUS_OK}
 */

typedef struct {
    msg_handle_type_t handle;
    msg_req_type_t    req_type;
    union {
        struct {
            msg_address_t     addr;
            msg_val_t         value;
        };
        struct {
            msg_address_t     start_addr;
            msg_address_t     end_addr;
        };
    };
} msg_req_t;

typedef struct {
    msg_handle_type_t handle;
    msg_req_type_t    req_type;
    msg_status_type_t status;
    msg_address_t     addr;
    msg_val_t         value;
} msg_resp_t;

typedef struct {
    char          * msg_req_buffer;
    char          * msg_resp_buffer;
    uint32_t      * msg_len;
    int             mem_fd;
} msg_parser_ctxt_t;

extern void msg_parser(char *req, char *resp, uint32_t *msg_len);
extern void msg_parser_init();
extern void msg_parser_munmap_all(void);

#endif


