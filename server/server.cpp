
#include <iostream>
#include <stdio.h>
#include <cstring>
#include <string>
#include <assert.h>
#include <pthread.h>
#include <time.h>
#include <stropts.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <ifaddrs.h>
#include <linux/netdevice.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>
#include "msg_parser.h"
#include "server.h"


server::server(uint32_t udp_port, uint32_t tcp_port, 
        uint8_t udp_repeat_timeout, uint8_t tcp_alive_timeout)
{
    this->server_udp_transmit_port   = udp_port;
    this->server_tcp_listen_port     = tcp_port;
    assert(udp_repeat_timeout>=UDP_REPEAT_TIMEOUT_THRESHOLD);
    this->udp_repeat_timeout         = udp_repeat_timeout;
    this->tcp_alive_timeout          = tcp_alive_timeout;
    this->connection_status          = UNCONNECTED;
    this->alive_elapsed_time         = 0;
    memset(this->hostIpAddr, 0x00, sizeof(this->hostIpAddr));
    this->client_socket_handle = this->server_socket_handle = this->udp_socket_handle = 0;
    this->gethost_itf_ipaddr((char *)this->hostIpAddr, sizeof(this->hostIpAddr), "wlan0");
}

void server::stop()
{
    pthread_cancel(udp_thread_id);
    pthread_cancel(tcp_thread_id);
}

void * server::start(void *ptr)
{
    int err_1, err_2;
    err_2 = pthread_create(&((server*)ptr)->udp_thread_id, NULL, &server::udp_thread, ptr);
    err_1 = pthread_create(&((server*)ptr)->tcp_thread_id, NULL, &server::tcp_thread, ptr);
    if (err_1!=0 || err_2!=0) {
        printf("threads creation failed\n");
    }
    pthread_join(((server*)ptr)->tcp_thread_id, NULL);
    pthread_join(((server*)ptr)->udp_thread_id, NULL);
    return 0;
}

void * server::udp_thread(void *ptr)
{
    printf("Starting udp_thread : PORT:%d\n", ((server*)ptr)->server_udp_transmit_port);
    ((server *)ptr)->udp_repeater_loop();
    return NULL;
}

void * server::tcp_thread(void *ptr)
{
    printf("Starting tcp_thread : PORT:%d\n", ((server*)ptr)->server_tcp_listen_port);
    ((server *)ptr)->tcp_processor_loop();
    return NULL;
}

server_connection_status server::get_connection_status()
{
    server_connection_status status;
    pthread_mutex_lock(&this->lock);
    {
        status = this->connection_status;
    }
    pthread_mutex_unlock(&this->lock);
    return status;
}

void server::set_connection_status(server_connection_status status)
{
    pthread_mutex_lock(&this->lock);
    {
        this->connection_status = status;
        printf("Connection status changed to %d \n", status);
    }
    pthread_mutex_unlock(&this->lock);
}

void server::gethost_itf_ipaddr(char *ip_addr, uint16_t len, std::string itf)
{
    struct ifaddrs * ifAddrStruct=NULL;
    struct ifaddrs * ifa=NULL;
    void * tmpAddrPtr=NULL;

    getifaddrs(&ifAddrStruct);
    for (ifa = ifAddrStruct; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr) {
            continue;
        }
        if (ifa->ifa_addr->sa_family == AF_INET) { // check it is IP4
            // is a valid IP4 Address
            tmpAddrPtr=&((struct sockaddr_in *)ifa->ifa_addr)->sin_addr;
            char addressBuffer[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, tmpAddrPtr, addressBuffer, INET_ADDRSTRLEN);
            if (strcmp(ifa->ifa_name, "eth0")==0) {
                strcpy(ip_addr, addressBuffer);
                printf("\n%s\n", ip_addr);
            }
        }
    }
    if (ifAddrStruct!=NULL) freeifaddrs(ifAddrStruct);
    if ((strlen(ip_addr)==0) && (strlen(ip_addr)<len)) {
        assert(0);
    }
}

void server::udp_thread_cancel(void *srv)
{
    printf("cancelling udp_thread\n");
    close(((server*)srv)->udp_socket_handle);
}

void server::tcp_thread_cancel(void *srv)
{
    printf("cancelling tcp_thread\n");
    if (((server*)srv)->client_socket_handle) {
        close(((server*)srv)->client_socket_handle);
        ((server*)srv)->client_socket_handle = 0;
    }
    close(((server*)srv)->server_socket_handle);
}

void server::udp_repeater_loop()
{
    /* Setup udp socket and broadcast message parameters */
    uint8_t status = 0;
    struct sockaddr_in udp_socket_addr;
    char broadcast_message[200];
    int yes = 1;

    this->udp_socket_handle = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
    assert(this->udp_socket_handle!=0);
    inet_pton(AF_INET, "255.255.255.255", &udp_socket_addr.sin_addr.s_addr);
    udp_socket_addr.sin_port = htons(this->server_udp_transmit_port);
    udp_socket_addr.sin_family = PF_INET;

        status |= setsockopt(this->udp_socket_handle, SOL_SOCKET, SO_BROADCAST, &yes, sizeof(int));

    if (status != 0) {
        printf("Error in udp socket creation \n");
    }

    sprintf(broadcast_message, "PROT : TCP, IP : %s, PORT : %d, MAX_MSG_LEN : %d \n", 
            this->hostIpAddr, this->server_tcp_listen_port, MSG_MAX_LEN);

    pthread_cleanup_push((server::udp_thread_cancel), this);

    while(1) {
        pthread_testcancel();
        if (this->get_connection_status()==UNCONNECTED) {
            /* Broadcast message */
            sendto(this->udp_socket_handle, broadcast_message, strlen(broadcast_message), 0, 
                (struct sockaddr *)&udp_socket_addr, sizeof(udp_socket_addr));
        }
        sleep(this->udp_repeat_timeout);
    }
    pthread_cleanup_pop(0);
}

void server::tcp_processor_loop()
{
    /* Start with unconnected state and listen for connections over TCP port specified via
     * server_tcp_listen_port
     */
    uint8_t status = 0;
    struct sockaddr_in server_socket_addr, client_socket_addr;
    socklen_t clilen = sizeof(client_socket_addr);
    char msg_recv_buffer[MSG_MAX_LEN*2];
    char msg_send_buffer[MSG_MAX_LEN*2];
    uint32_t msg_len;
    bool reconnect_client = false;
    fd_set sockets_set;
    struct timeval tv;
    memset((char *)&server_socket_addr, 0, sizeof(server_socket_addr));
    server_socket_addr.sin_family = AF_INET;
    server_socket_addr.sin_addr.s_addr = inet_addr(hostIpAddr);
    server_socket_addr.sin_port = htons(this->server_tcp_listen_port);
    this->server_socket_handle = socket(AF_INET, SOCK_STREAM, 0);
    assert(this->server_socket_handle!=0);

    status |= bind(this->server_socket_handle, (struct sockaddr *) &server_socket_addr, 
        sizeof(server_socket_addr));

    assert(status==0);
    /* Listen on TCP socket with max of 1 pending connection */
    status = listen(this->server_socket_handle, 1);

    pthread_cleanup_push((server::tcp_thread_cancel), this);

    while(1) {
        this->client_socket_handle = accept(this->server_socket_handle,
            (struct sockaddr *)&client_socket_addr, &clilen);
        assert(this->client_socket_handle!=0);
        FD_ZERO(&sockets_set);
        FD_SET(this->client_socket_handle, &sockets_set);
        this->set_connection_status(CONNECTED);
        while (1) {
            /* Msg processor loop */

            /* Wait first to receive msg length header */
            /* Length value encoding used for TCP connections
             * length = 2 bytes
             * value  = n bytes as indicated by length field 
             */
            while (1) {
                uint32_t num_recv;
                memset(msg_recv_buffer, 0x00, sizeof(msg_recv_buffer));
                memset(msg_send_buffer, 0x00, sizeof(msg_send_buffer));
                /* Wait for socket to be readable */
                tv.tv_sec  = TCP_SOCKET_RECV_TIMEOUT;
                tv.tv_usec = 0;
                if (select(FD_SETSIZE, &sockets_set, NULL, NULL, &tv) > 0) {
                    if((num_recv=recv(this->client_socket_handle, msg_recv_buffer, MSG_LEN_FIELD_LEN,
                        0)) != MSG_LEN_FIELD_LEN) {
                        /* Timeout while waiting for msg process request,
                         * increment alive_elapsed_time
                         */
                        this->alive_elapsed_time++;
                        printf("Elapsed time : %d\n", this->alive_elapsed_time);
                    } else {
                        /* Msg header length received successfully, proceed to msg decoding */
                        reconnect_client = false;
                        this->alive_elapsed_time = 0;
                        break;
                    }
                } else {
                    this->alive_elapsed_time++;
                    printf("Elapsed time : %d\n", this->alive_elapsed_time);
                }

                if (num_recv==0) {
                    printf("Client disconnected from connection \n");
                    reconnect_client = true;
                }

                if (this->alive_elapsed_time > 
                        this->tcp_alive_timeout/TCP_SOCKET_RECV_TIMEOUT) {
                    printf("Disconnecting client for lack of interactions\n");
                    reconnect_client = true;
                }

                if (reconnect_client) {
                    close(this->client_socket_handle);
                    this->client_socket_handle = 0;
                    set_connection_status(UNCONNECTED);
                    break;
                }
            }
	  
            if (reconnect_client) {
                break; /* Since connection was timedout */
            } else {
                /* MSB to LSB ordering */
                msg_len = *(uint16_t*)msg_recv_buffer;
                if (recv(this->client_socket_handle, msg_recv_buffer, msg_len,
                    MSG_WAITALL) != (int16_t)msg_len) {
                    /* Socket timeout, terminate connection and repeat */
                    close(this->client_socket_handle);
                    this->client_socket_handle = 0;
                    this->set_connection_status(UNCONNECTED);
                    break;
                } else {
                    /* Msg received successfully into msg_recv_buffer, start parsing it */
	                msg_parser(msg_recv_buffer, msg_send_buffer+MSG_LEN_FIELD_LEN, &msg_len);
		            *(uint16_t*)msg_send_buffer = msg_len;
                    if (write(this->client_socket_handle, msg_send_buffer, 
                        msg_len+MSG_LEN_FIELD_LEN) != (int16_t)(msg_len+MSG_LEN_FIELD_LEN)) {
                    }
                }
            }
        }
    }
    pthread_cleanup_pop(0);
}

