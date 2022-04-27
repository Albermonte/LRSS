# main_select.py

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
# Timeout in seconds
TIMEOUT = 10
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
is_timeout = False

# List of sockets for select.select()
sockets_list = [sock]

while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list, TIMEOUT)

    notified_socket: socket.socket
    for notified_socket in read_sockets:
        if notified_socket == sock:

            # Accept new connection
            client_socket, client_address = sock.accept()

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

        else:
            # We are active so no restart timeout
            is_timeout = False

            req = notified_socket.recv(RECV_BUFFER).decode()

            # Check if keep-alive header is present
            keep_alive = re.search('Connection: keep-alive', req)
            res = Res(notified_socket, "HTTP/1.1", not not keep_alive)

            # Check if request is valid
            result = re.search('(GET|HEAD)(.*) HTTP/', req)
            if not result:
                res.not_found()
                notified_socket.close()
                sockets_list.remove(notified_socket)
                continue

            # Remove first space from regex result
            req_file = result.group(2).lstrip()

            # Get requested file and redirect to index.html if no file requested
            if req_file == "/":
                req_file = "/index.html"
            # If not found, send 404
            elif not req_file:
                # Default 404 file if none present in public folder
                req_file = "/404.html"


            filename = "./public" + req_file
            # Check if request method is HEAD and send only the headers
            head_only = result.group(1) == "HEAD"
            r = res.send(filename, not not head_only)

            # If keep-alive header is not present, close the socket
            # If send returned -1 (file not found), close the socket
            if not keep_alive or r == -1:
                notified_socket.close()
                sockets_list.remove(notified_socket)

    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

    if not (read_sockets or exception_sockets):
        if not is_timeout:
            print("Servidor web inactivo")
            # Timeout to true to not send the innactive message every 10 seconds
            is_timeout = True
            for notified_socket in sockets_list:
                if notified_socket != sock:
                    notified_socket.close()
                    sockets_list.remove(notified_socket)


# Source:
#   https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
#   https://iximiuz.com/en/posts/writing-web-server-in-python-sockets/
#   https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
#   https://medium.com/geekculture/implementing-http-from-socket-89d20a1f8f43
