// ping_oc.c

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <netdb.h>
#include <ctype.h>

#define MSG_AMOUNT 3

int sock;

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
    printf("## OC CLIENT ## \n\n");
    if (argc < 3)
    {
        printf("Missing params.\n");
        exit(EXIT_FAILURE);
    }

    if (!isNumber(argv[2]))
    {
        printf("Port \"%s\" not numeric, usage: ./ping_noc.out host port\n", argv[2]);
        exit(EXIT_FAILURE);
    }

    printf("Pinging to: %s, %s \n", argv[1], argv[2]);
    printf("Press ENTER key to Continue\n");
    getchar();

    struct sockaddr_in server_address;
    socklen_t addrlen = sizeof(server_address);
    int port = atoi(argv[2]);
    char data_received[1024];
    memset(data_received, 0, sizeof(data_received)); // Clear buffer

    printf("Creating socket\n");
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
        printf("Error creating socket\n");
        exit(EXIT_FAILURE);
    }

    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z

    server_address.sin_family = AF_INET;   // IPv4 address family
    server_address.sin_port = htons(port); // Port number at which the server is listning

    // Get IP from host
    struct hostent *hostname = gethostbyname(argv[1]);
    if (!hostname)
    {
        printf("Can't resolve hostname %s\n", argv[1]);
    }
    bcopy(hostname->h_addr, &server_address.sin_addr, hostname->h_length);

    // Al ser TCP tenemos que conectarnos primero al servidor antes de enviar paquetes
    if (connect(sock, (struct sockaddr *)&server_address, addrlen) < 0)
    {
        printf("Connection failed\n");
        exit(EXIT_FAILURE);
    }
    printf("Connection successful\n\n");

    int msg_count = 0,
        valread;
    double time[MSG_AMOUNT];
    struct timeval start, stop;
    double msecs = 0;
    double total_time = 0;
    char *msg = "a";

    printf("Pinging to %s with a total of %ld bytes:\n\n", argv[1], strlen(msg) * MSG_AMOUNT);
    while (msg_count < MSG_AMOUNT)
    {
        // 1 char = 1 byte
        printf("Sending ping %d of %ld bytes...\t", msg_count, strlen(msg));
        gettimeofday(&start, NULL);
        // Una vez conectados, enviamos el mensaje
        send(sock, msg, strlen(msg), 0);
        // Esperamos a la respuesta del servidor
        valread = read(sock, data_received, 1024);
        gettimeofday(&stop, NULL);

        if (strcmp(msg, data_received))
        {
            printf("Data received from server is not consistent\n");
            exit(EXIT_FAILURE);
        }

        msecs = (double)(stop.tv_usec - start.tv_usec) / 1000;
        printf("...ping %d finished, took: %f ms\n", msg_count, msecs);
        total_time += msecs;
        msg_count++;
        memset(data_received, 0, sizeof(data_received)); // Clear buffer
    }

    printf("\n## Total Time for %d pings: %f ms, Mean: %f ms ##\n\n", msg_count, total_time, (total_time / msg_count));

    close(sock);
}

// Fuentes:
// https://www.tutorialspoint.com/c_standard_library/c_function_signal.htm
// https://github.com/dheeraj-2000/task2_computernetworks/blob/master/Multithreaded_TCP_Server_Client/server.cpp
