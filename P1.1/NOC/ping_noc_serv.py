# ping_noc_serv.py

import sys
import signal
import socket

# Comprobamos que haya el número de parámetros requerido
if len(sys.argv) < 2:
    print("Missing param PORT.\n")
    quit()

# Convertir la entrada de texto a entero
PORT = int(sys.argv[1])
print(f"Running server on Port: {PORT}")

print("Creating Socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


# Definismos la señal para Ctrl+C después de crear el socket para así poder cerrarlo luego
signal.signal(signal.SIGINT, sig_handler)

print("Binding address and port")
# Bindeamos el host y puerto a la dirección del servidor
server_address = ('localhost', PORT)
sock.bind(server_address)

# while True para quedarnos a la escucha de nuevos clientes cuando el actual se desconecte
while True:
    print("Waiting for connection")
    # Esperamos a un mensaje
    data, client_address = sock.recvfrom(1024)

    if data:
        print(f"Receiving data from {client_address}... Sending back")
        # Una vez recivido lo enviamos de vuelta
        sock.sendto(data, client_address)
