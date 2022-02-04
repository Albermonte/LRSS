#include <stdio.h>

void main(int argc, char *argv[])
{
    if (argc < 3)
    {
        printf("Faltan parámetros.\n");
    }
    printf("%s, %s", argv[1], argv[2]);
}
