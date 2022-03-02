# ping_oc_serv.py

import sys
import signal
import socket

if len(sys.argv) < 2:
    print("Missing param PORT.\n")
    quit()

PORT = int(sys.argv[1])
print(f"Running server on Port: {PORT}")

print("Creating Socket")
# SOCK_STREAM ya que es TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

print("Binding address and port")
server_address = ('localhost', PORT)
sock.bind(server_address)

print("Listening...")
# En esta ocasión quedamos a la escucha para más tarde aceptar la conexión desde el servidor
sock.listen()

# while True para quedarnos a la escucha de nuevos clientes cuando el actual se desconecte
while True:
    print("Waiting for connection")
    # Esperamos a la conexión desde el cliente, dentro de un while para poder escuchar a más
    # clientes una vez el actual se desconecte
    connection, client_address = sock.accept()

    print(f"Connectiong from {client_address}")

    while True:
        # Esperamos a los parques enviados por el cliente
        data = connection.recv(1024)
        # Si no obtenemos nada salimos del bucle
        if not data:
            break
        print("Msg received... Sending back")
        # Reenviamos lo recibido de nuevo hacia el cliente ("pong")
        connection.sendall(data)
