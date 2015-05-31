#ifndef _SERVER_H_

using std::string;

typedef enum {
    CONNECTED,
    UNCONNECTED,
} server_connection_status;

#define IP_ADDR_LEN 100
#define MSG_LEN_FIELD_LEN 2
#define MSG_MAX_LEN     200

#define TCP_SOCKET_RECV_TIMEOUT 10
#define UDP_REPEAT_TIMEOUT_THRESHOLD 2

/* UDP Message format
 * Message = "PROT : TCP, IP : {ip_address in xxx.xxx.xxx.xxx format}, PORT : {x}, MAX_MSG_LEN : {x}"
 * Repeated over UDP broadcast every udp_repeat_timeout
 */

/* TCP Message format
 * Message = "{length_field}{value of length length_field}"
 *      - length_field is of length MSG_LEN_FIELD_LEN
 *      - length_field value can be upto MAX_MSG_LEN
 */

class server;

class server {
    public :
        static void * start(void *);
        server(uint32_t udp_port, uint32_t tcp_port, uint8_t udp_repeat_timeout, 
                uint8_t tcp_alive_timeout, const char *);
        void stop();
    private :
        int server_socket_handle, client_socket_handle;
        int udp_socket_handle;
        pthread_t udp_thread_id, tcp_thread_id;
        static void * udp_thread(void *);
        static void * tcp_thread(void *);
        static void udp_thread_cancel(void *);
        static void tcp_thread_cancel(void *);
        char hostIpAddr[IP_ADDR_LEN];
        uint32_t server_udp_transmit_port;
        uint32_t server_tcp_listen_port;
        uint32_t udp_repeat_timeout;
        uint32_t tcp_alive_timeout;
        uint8_t  alive_elapsed_time;
        pthread_mutex_t lock;
        server_connection_status connection_status;
        server_connection_status get_connection_status();
        void gethost_itf_ipaddr(char *ip_addr, uint16_t len, const char * itf);
        void set_connection_status(server_connection_status status);
        void udp_repeater_loop();
        void tcp_processor_loop();
};

#endif
