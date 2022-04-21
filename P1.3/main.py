import sys
import signal
import socket
import select
import re
from utils.res import Res


if len(sys.argv) < 2:
    print("Missing param PORT.\n")
    quit()

RECV_BUFFER = 1024
PORT = int(sys.argv[1])
print(f"Running server on Port: {PORT}")

# Create socket
# Listen for new clients
# Send array of user info with connections to clients

print("Creating Socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

# Reuse address, no more address already in use error
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Binding address and port")
server_address = ('0.0.0.0', PORT)
sock.bind(server_address)

print("Listening...")
sock.listen()

while True:
    conn, addr = sock.accept()
    req = conn.recv(RECV_BUFFER).decode()
    res = Res(conn)
    # print(req)
    result = re.search('GET (.*) HTTP/', req)
    if not result:
        res.not_found()
        conn.close()
        continue

    req_file = result.group(1)
    if req_file == "/":
        req_file = "/index.html"

    # Línea de estado que contiene la versión del protocolo HTTP (por ejemplo, versión 1.0), el código de
    # respuesta (por ejemplo 200) y una palabra/frase explicativa.
    # Una serie de cabeceras HTTP.
    # Una línea en blanco.
    # Objeto solicitado, en caso de que exista

    filename = "./public" + req_file
    res.send(filename)

    conn.close()


# Source:
#   https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
#   https://iximiuz.com/en/posts/writing-web-server-in-python-sockets/
#   https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
#   https://medium.com/geekculture/implementing-http-from-socket-89d20a1f8f43
