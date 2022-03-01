#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <netdb.h>
#include <ctype.h>

#define MSG_AMOUNT 3

int sock;

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

int isNumber(char s[])
{
    printf("Checking port\n");
    for (int i = 0; s[i] != '\0'; i++)
    {
        if (isdigit(s[i]) == 0)
        {
            return 0;
        }
    }
    return 1;
}

void main(int argc, char *argv[])
{
    printf("## NOC CLIENT ## \n\n");
    if (argc < 3)
    {
        printf("Missing params.\n");
        exit(EXIT_FAILURE);
    }

    if (!isNumber(argv[2]))
    {
        printf("Port \"%s\" not recognized, usage: ./ping_noc.out host port\n", argv[2]);
        exit(EXIT_FAILURE);
    }

    printf("Pinging to: %s, %s \n", argv[1], argv[2]);
    printf("Press ENTER key to Continue\n");
    getchar();

    struct sockaddr_in server_address, client_address;
    socklen_t addrlen = sizeof(server_address);
    int port = atoi(argv[2]);
    char data_received[1024];
    memset(data_received, 0, sizeof(data_received)); // clear buffer

    printf("Creating socket\n");
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        printf("Error creating socket\n");
        exit(EXIT_FAILURE);
    }

    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z

    client_address.sin_family = AF_INET;                // IPv4 address family
    client_address.sin_addr.s_addr = htonl(INADDR_ANY); // Give the local machine address

    printf("Binding socket\n");
    if (bind(sock, (struct sockaddr *)&client_address, sizeof(client_address)) < 0)
    {
        printf("Binding socket failed\n");
        exit(EXIT_FAILURE);
    }

    server_address.sin_family = AF_INET;   // IPv4 address family
    server_address.sin_port = htons(port); // Port number at which the server is listning

    // Get IP from host
    struct hostent *hostname = gethostbyname(argv[1]);
    if (!hostname)
    {
        printf("Can't resolve hostname %s\n", argv[1]);
    }
    bcopy(hostname->h_addr, &server_address.sin_addr, hostname->h_length);

    int msg_count = 0;
    double time[MSG_AMOUNT];
    struct timeval start, stop;
    double msecs = 0;
    char *msg = "a";

    // TODO: Mean time, total time, etc
    while (msg_count < MSG_AMOUNT)
    {
        printf("Sending ping %d...\t", msg_count);
        // Send udp packet to server
        gettimeofday(&start, NULL);
        sendto(sock, msg, strlen(msg), 0, (struct sockaddr *)&server_address, addrlen);

        // Wait for the reply from the server
        if (recvfrom(sock, data_received, 1024, 0, (struct sockaddr *)&server_address, &addrlen) < 0)
        {
            printf("Error receiving data from server\n");
            exit(EXIT_FAILURE);
        }

        if (strcmp(msg, data_received))
        {
            printf("Data received from server is not consistent\n");
            exit(EXIT_FAILURE);
        }

        gettimeofday(&stop, NULL);
        msecs = (double)(stop.tv_usec - start.tv_usec) / 1000;
        printf("...ping %d finished, took: %f ms\n", msg_count, msecs);
        msg_count++;
        memset(data_received, 0, sizeof(data_received)); // clear buffer
    }
}

// Mejoras: multihilo? enviar identificador por mensaje
