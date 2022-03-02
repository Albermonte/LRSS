// ping_noc_serv.c

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>

// File descriptor del socket a crear
int sock;

void sig_handler(int signum)
{
    if (signum == SIGINT || signum == SIGTSTP)
    {
        printf("Closing %d\n", signum);
        // Cerrar el socket cuando el usuario presiona Ctrl+C o Ctrl+Z
        close(sock);
        exit(EXIT_SUCCESS);
    }
}

void main(int argc, char *argv[])
{
    printf("## NOC SERVER ## \n\n");
    // Comprobamos que haya el número de parámetros requerido
    if (argc < 2)
    {
        printf("Missing param PORT.\n");
        exit(EXIT_FAILURE);
    }

    // Estructuras para guardar las direcciones de cliente y servidor
    struct sockaddr_in server_address, client_address;
    socklen_t addrlen = sizeof(client_address);
    // Convertir la entrada de texto a entero para que pueda ser leido por htons
    int port = atoi(argv[1]);
    char data_received[1024];
    // Limpiamos buffer para que no aparezcan caracteres extraños
    memset(data_received, 0, sizeof(data_received));

    printf("Listening on %d\n", port);

    // Creamos el socket
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

    // Definimos las señales para Ctrl+C y Ctrl+Z después de crear el socket para así poder cerrarlo luego
    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z

    server_address.sin_family = AF_INET;                // IPv4 address family
    server_address.sin_addr.s_addr = htonl(INADDR_ANY); // Give the local machine address
    server_address.sin_port = htons(port);              // Port at which server listens to the requests

    // Bindeando socket al puerto especificado por el usuario
    printf("Binding socket\n");
    if (bind(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0)
    {
        printf("Binding socket to port %d failed\n", port);
        exit(EXIT_FAILURE);
    }

    // Esperar al mensaje desde el cliente
    printf("Waiting for msg...\n");
    while (1)
    {
        // Dentro del while para poder quedarnos escuchando siempre
        if (recvfrom(sock, data_received, 1024, 0, (struct sockaddr *)&client_address, &addrlen) < 0)
        {
            printf("Error receiving data from client\n");
            exit(EXIT_FAILURE);
        }

        printf("Msg received..\tSending msg back\n");

        // Des comentar la siguiente linea para ver si la verificación del cliente funciona
        // strcpy(data_received, "b");

        // Una vez recibido el mensaje lo reenviaremos al cliente para hacer la parte "pong" del "ping"
        sendto(sock, data_received, strlen(data_received), 0, (struct sockaddr *)&client_address, addrlen);

        memset(data_received, 0, sizeof(data_received)); // Clear buffer
    }
    // El servidor se quedará escuchando permanentemente hasta que se produzca la interrupción por teclado
}

// Fuentes:
// https://tutorialspoint.dev/language/cpp/socket-programming-cc
// https://www.ibm.com/docs/en/zos/2.4.0?topic=sockets-using-sendto-recvfrom-calls
// https://www.tutorialspoint.com/c_standard_library/c_function_signal.htm
// https://www.gnu.org/software/libc/manual/html_node/Local-Socket-Example.html
// https://www.gnu.org/software/libc/manual/html_node/Socket-Addresses.html
// https://www.gnu.org/software/libc/manual/html_node/Inet-Example.html
// https://github.com/dheeraj-2000/task2_computernetworks/tree/master/udp
