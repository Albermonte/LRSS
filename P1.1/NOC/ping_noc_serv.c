#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>

int sock;

// https://www.tutorialspoint.com/c_standard_library/c_function_signal.htm
void sig_handler(int signum)
{
    if (signum == SIGINT)
    {
        printf("Closing %d", signum);
        close(sock);
        exit(1);
    }
}

// https://www.gnu.org/software/libc/manual/html_node/Local-Socket-Example.html
void main(int argc, char *argv[])
{
    printf("## NOC SERVER ## \n\n");
    if (argc < 2)
    {
        printf("Missing param PORT.\n");
        exit(EXIT_FAILURE);
    }

    // https://www.gnu.org/software/libc/manual/html_node/Socket-Addresses.html
    // https://www.gnu.org/software/libc/manual/html_node/Inet-Example.html
    struct sockaddr_in server_address;
    struct sockaddr_in client_address;
    int port = atoi(argv[1]);
    char data_received[1024];

    printf("Listening on %d\n", port);

    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z
    // Create the socket.
    /**
     * socket(domain, type, protocol)
     * domain: PF_LOCAL, AF_INET (IPv4), AF_INET6 (IPv6)
     * type: SOCK_STREAM (TCP), SOCK_DGRAM (UDP)
     * protocol: 0 (IP), more at /etc/protocols
     */
    printf("Creating socket\n");
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        printf("Error creating socket\n");
        exit(EXIT_FAILURE);
    }

    server_address.sin_family = AF_INET;                // IPv4 address family
    server_address.sin_addr.s_addr = htonl(INADDR_ANY); // Give the local machine address
    server_address.sin_port = htons(port);              // Port at which server listens to the requests

    // Binding socket to specified port
    printf("Binding socket\n");
    if (bind(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0)
    {
        printf("Binding socket to port %d failed\n", port);
        exit(EXIT_FAILURE);
    }

    // Receive msg from client
    // https://www.ibm.com/docs/en/zos/2.4.0?topic=sockets-using-sendto-recvfrom-calls
    printf("Waiting for msg...\n");
    if (recvfrom(sock, data_received, sizeof(data_received), 0, &client_address, sizeof(client_address)) < 0)
    {
        printf("Error receiving data from client\n");
        exit(EXIT_FAILURE);
    }

    printf("Msg received:\n %s", data_received);
}

// https://tutorialspoint.dev/language/cpp/socket-programming-cc
