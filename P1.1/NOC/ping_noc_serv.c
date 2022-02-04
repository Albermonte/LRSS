#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>

// https://www.gnu.org/software/libc/manual/html_node/Local-Socket-Example.html
void main(int argc, char *argv[])
{
    printf("## NOC SERVER ## \n\n");
    if (argc < 2)
    {
        printf("Faltan parámetros.\n");
    }

    int host = atoi(argv[1]);
    // https://www.gnu.org/software/libc/manual/html_node/Socket-Addresses.html
    // https://stackoverflow.com/questions/3689925/struct-sockaddr-un-vs-sockaddr
    struct sockaddr address;

    // Test msg
    char *msg = "Hello from client";

    printf("%d\n", host);
}

// https://tutorialspoint.dev/language/cpp/socket-programming-cc