#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>

int sock;

// https://ubidots.com/blog/how-to-simulate-a-tcpudp-client-using-netcat/
// https://www.tutorialspoint.com/c_standard_library/c_function_signal.htm
void sig_handler(int signum)
{
    if (signum == SIGINT || signum == SIGTSTP)
    {
        printf("Closing %d\n", signum);
        close(sock);
        exit(EXIT_SUCCESS);
    }
}

// https://www.gnu.org/software/libc/manual/html_node/Local-Socket-Example.html
void main(int argc, char *argv[])
{
    printf("## OC SERVER ## \n\n");
    if (argc < 2)
    {
        printf("Missing param PORT.\n");
        exit(EXIT_FAILURE);
    }

    // https://www.gnu.org/software/libc/manual/html_node/Socket-Addresses.html
    // https://www.gnu.org/software/libc/manual/html_node/Inet-Example.html
    struct sockaddr_in server_address;
    socklen_t addrlen = sizeof(server_address);
    int port = atoi(argv[1]);
    char data_received[1024];
    memset(data_received, 0, sizeof(data_received)); // Clear buffer

    printf("Listening on %d\n", port);

    // Create the socket.
    /**
     * socket(domain, type, protocol)
     * domain: PF_LOCAL, AF_INET (IPv4), AF_INET6 (IPv6)
     * type: SOCK_STREAM (TCP), SOCK_DGRAM (UDP)
     * protocol: 0 (IP), more at /etc/protocols
     */
    printf("Creating socket\n");
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
        printf("Error creating socket\n");
        exit(EXIT_FAILURE);
    }

    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z

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

    // The backlog argument defines the maximum length to which the
    // queue of pending connections for sockfd may grow
    if ((listen(sock, 3)) < 0)
    {
        printf("Listen failed\n");
        exit(EXIT_FAILURE);
    }

    printf("Waiting for msg...\n");
    int new_socket, valread;

    while (1)
    {
        if ((new_socket = accept(sock, (struct sockaddr *)&server_address, (socklen_t *)&addrlen)) < 0)
        {
            printf("Eror %d", new_socket);
            exit(EXIT_FAILURE);
        }
        while (1)
        {
            valread = read(new_socket, data_received, 1024);
            if (!valread)
                break;

            printf("Msg received..\tSending msg back\n");

            // Uncomment to check if client verification works
            // strcpy(data_received, "b");

            send(new_socket, data_received, strlen(data_received), 0);
            memset(data_received, 0, sizeof(data_received)); // Clear buffer
        }
    }
}
