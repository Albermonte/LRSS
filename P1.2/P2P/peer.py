# peer.py

import errno
import signal
import sys
import select
import socket
import json


def delete_last_line():
    # Delete last line from stdout
    sys.stdout.write('\x1b[2K')


if len(sys.argv) < 3:
    print("Missing params.\n")
    quit()

if not sys.argv[2].isnumeric():
    print(
        f"Port \"{sys.argv[2]}\" not numeric, usage: python3 ping_oc.py host port\n")
    quit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])
RECV_BUFFER = 1024

print(f"Running client on {HOST}:{PORT}\n")

# Connect to server
# Receive list of clients
# Connect to every client

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
# Set recv to not blocking so we can do things while waiting for msg
# sock.setblocking(False)

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Assigning free port https://stackoverflow.com/a/1365284/7312697
sock_server.bind(("", 0))
# Reuse address, no more address already in use error
sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock_server.setblocking(False)
sock_server.listen(50)
print(f"Socket server on: {sock_server.getsockname()}")


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


def delete_last_line():
    # Delete last line from stdout
    sys.stdout.write('\x1b[2K')


def receive_message(client_socket: socket.socket):
    try:
        data = client_socket.recv(RECV_BUFFER)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(data):
            return False

        data = data.decode('utf-8')
        data = json.loads(data)

        return data

    except Exception as e:
        print("Error receiving msg")
        print(e)
        # Some error or disconection
        return False


def connect_to_peers(sock: socket.socket):
    data_received = sock.recv(RECV_BUFFER)
    # The server was closed
    if not len(data_received):
        print("Connection lost")
        sig_handler(0, 0)

    # Convert string to json
    data_received = data_received.decode('utf-8')
    data_received = json.loads(data_received)
    # Deleting our peer
    if data_received[username]:
        del data_received[username]
    client_connections_list = data_received
    print(client_connections_list)
    for client_name in client_connections_list:
        conn = client_connections_list[client_name]
        ip = conn[0]
        port = conn[1]
        print(f"Connecting to {ip}:{port}")
        new_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_socket.connect((ip, port))
            sockets_list.append(new_socket)
        except Exception as e:
            print(f"Error connecting to {ip}:{port}")
            print(str(e))
            new_socket.close()


signal.signal(signal.SIGINT, sig_handler)

# Ask user for username
username = input("Enter your username: ")
if not username:
    username = "Anonymous"
print(f"You choosed {username} as username \n\n")

# First message for server
data = {
    "username": username,
    "port": sock_server.getsockname()[1]
}
# Convert to json and send
data_send = json.dumps(data)
data_send = bytes(data_send, "utf-8")

sock.send(data_send)

sockets_list = [sock_server, sys.stdin]
client_connections_list = {}

print("Connecting to peers")

connect_to_peers(sock)

print("###### Connected ######\n\n")
print("You > ", end="", flush=True)

while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], [])

    notified_socket: socket.socket
    for notified_socket in read_sockets:

        if notified_socket == sock_server:
            # Some client is sending a message
            client_socket, client_address = sock_server.accept()
            # Receive message
            sockets_list.append(client_socket)
            delete_last_line()
            print(f"New peer connected {client_socket.getsockname()}")
            print("You > ", end="", flush=True)

        elif notified_socket == sys.stdin:
            # Not a socket, instead it's the user writing something
            message = sys.stdin.readline().strip()

            # If not message (eg: \n) don't send it
            if message:
                # TODO: Check if message + username + data > RECV_BUFFER
                data["message"] = message
                # print(f"Sending {data}")
                data_send = json.dumps(data)
                data_send = bytes(data_send, "utf-8")
                peer: socket.socket
                for peer in sockets_list:
                    if peer != sock_server and peer != sys.stdin:
                        peer.send(data_send)
                print("You > ", end="", flush=True)
        else:
            # Peer sending msg
            message = receive_message(notified_socket)
            if not message:
                # Peer disconnected
                delete_last_line()
                print(f"Peer disconnected {notified_socket.getsockname()}")
                print("You > ", end="", flush=True)
                sockets_list.remove(notified_socket)
                continue

            delete_last_line()
            print(f"{message['username']} : {message['message']}")
            print("You > ", end="", flush=True)
