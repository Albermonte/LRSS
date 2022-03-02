// ping_noc.c

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

// Definimos el número de mensajes a mandar para poder cambiarlo fácilmente
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
    printf("## NOC CLIENT ## \n\n");
    // Comprobamos que haya el número de parámetros requerido
    if (argc < 3)
    {
        printf("Missing params.\n");
        exit(EXIT_FAILURE);
    }

    // Comprobamos que el puerto sea un número, si no lo es podría producir un "Core dump" al asignarlo al socket
    if (!isNumber(argv[2]))
    {
        printf("Port \"%s\" not numeric, usage: ./ping_noc.out host port\n", argv[2]);
        exit(EXIT_FAILURE);
    }

    printf("Pinging to: %s, %s \n", argv[1], argv[2]);
    // Esperamos a la acción del usuario para crear el socket y lanzar el ping
    printf("Press ENTER key to Continue\n");
    getchar();

    // Estructuras para guardar las direcciones de cliente y servidor
    struct sockaddr_in server_address, client_address;
    socklen_t addrlen = sizeof(server_address);
    // Convertir la entrada de texto a entero para que pueda ser leido por htons
    int port = atoi(argv[2]);
    char data_received[1024];
    // Limpiamos buffer para que no aparezcan carácteres extraños
    memset(data_received, 0, sizeof(data_received)); // Clear buffer

    printf("Creating socket\n");
    // Creamos el socket
    /**
     * socket(domain, type, protocol)
     * domain: PF_LOCAL, AF_INET (IPv4), AF_INET6 (IPv6)
     * type: SOCK_STREAM (TCP), SOCK_DGRAM (UDP)
     * protocol: 0 (IP), more at /etc/protocols
     */
    // La diferencia con el socket TCP está en el parámetro SOCK_DGRAM que se usa en UDP, mientras en TCP se usa SOCK_STREAM
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        printf("Error creating socket\n");
        exit(EXIT_FAILURE);
    }

    // Definismos las señales para Ctrl+C y Ctrl+Z después de crear el socket para así poder cerrarlo luego
    signal(SIGINT, sig_handler);  // handle ctrl+c
    signal(SIGTSTP, sig_handler); // handle ctrl+z

    client_address.sin_family = AF_INET;                // IPv4 address family
    client_address.sin_addr.s_addr = htonl(INADDR_ANY); // Give the local machine address

    printf("Binding socket\n\n");
    if (bind(sock, (struct sockaddr *)&client_address, sizeof(client_address)) < 0)
    {
        printf("Binding socket failed\n");
        exit(EXIT_FAILURE);
    }

    server_address.sin_family = AF_INET;   // IPv4 address family
    server_address.sin_port = htons(port); // Port number at which the server is listning

    // Convertimos el host en una IP
    struct hostent *hostname = gethostbyname(argv[1]);
    if (!hostname)
    {
        printf("Can't resolve hostname %s\n", argv[1]);
    }
    // Copiamos esta IP a la dirección del servidor
    bcopy(hostname->h_addr, &server_address.sin_addr, hostname->h_length);

    int msg_count = 0;
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

        // Guardamos el tiempo actual
        gettimeofday(&start, NULL);
        // Enviamos el paquete udp al servidor
        sendto(sock, msg, strlen(msg), 0, (struct sockaddr *)&server_address, addrlen);

        // Quedamos a la espera de la respuesta desde el servidor
        if (recvfrom(sock, data_received, 1024, 0, (struct sockaddr *)&server_address, &addrlen) < 0)
        {
            printf("Error receiving data from server\n");
            exit(EXIT_FAILURE);
        }
        // Guardamos el tiempo actual, otra vez
        gettimeofday(&stop, NULL);

        // Como mejora, comprobamos que el mensaje enviado y recibido sea el mismo. Si no lo es, algo raro estaría pasando.
        // MITM, servidor equivocado, algun error en el servidor...
        if (strcmp(msg, data_received))
        {
            printf("Data received from server is not consistent\n");
            exit(EXIT_FAILURE);
        }

        // Cálculos para obtener los ms que ha pasado desde que enviamos hasta que recibimos el paquete
        msecs = (double)(stop.tv_usec - start.tv_usec) / 1000;
        printf("...ping %d finished, took: %f ms\n", msg_count, msecs);
        total_time += msecs;
        msg_count++;
        memset(data_received, 0, sizeof(data_received)); // Clear buffer
    }

    // Cálculos finales para mostrar al usuario algunas estadísticas extra
    printf("\n## Total Time for %d pings: %f ms, Mean: %f ms ##\n\n", msg_count, total_time, (total_time / msg_count));
    // Finalmente cerramos el socket
    close(sock);
}

// Fuentes:
// https://www.tutorialspoint.com/c_standard_library/c_function_signal.htm
// https://github.com/dheeraj-2000/task2_computernetworks/tree/master/udp
// https://www.codegrepper.com/code-examples/c/check+if+string+is+number+c
