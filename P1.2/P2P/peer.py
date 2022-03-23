# peer.py

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

print(f"Running client on {HOST}:{PORT}\n")

# Connect to server
# Receive list of clients
# Connect to every client

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
# Set recv to not blocking so we can do things while waiting for msg
# sock.setblocking(False)


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

# Ask user for username
username = input("Enter your username: ")
if not username:
    username = "Anonymous"
print(f"You choosed {username} as username \n\n")

# First message for server
data = {
    "username": username,
    "message": "connecting"
}
# Convert to json and send
data_send = json.dumps(data)
data_send = bytes(data_send, "utf-8")

sock.send(data_send)

print("###### Connected ######\n\n")

sockets_list = [sock]
client_list = {}
client_connections_list = {}


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        if notified_socket == sock:
            data_received = sock.recv(1024)
            # The server was closed
            if not len(data_received):
                print("Connection lost")
                sig_handler(0, 0)

            # Convert string to json
            data_received = data_received.decode('utf-8')
            data_received = json.loads(data_received)
            if data_received[username]:
                del data_received[username]
                client_connections_list = data_received
                print(client_connections_list)
                for client_name in client_connections_list:
                    conn = client_connections_list[client_name]
                    ip = conn[0]
                    port = conn[1]
                    print("Listening...")
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # TODO: Address already in use
                    print(f"Port: {port}")
                    server_socket.bind((ip, port)) 
                    server_socket.listen()
                    sockets_list.append(server_socket)
            else:
                # Message from client
                pass


# Source: https://github.com/engineer-man/youtube/blob/master/141/client.py
