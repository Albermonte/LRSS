import sys
import signal
import socket
import select
import json

if len(sys.argv) < 2:
    print("Missing param PORT.\n")
    quit()

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
server_address = ('localhost', PORT)
sock.bind(server_address)

print("Listening...")
sock.listen()

# List of sockets for select.select()
sockets_list = [sock]

# List of clients
client_list = {}
client_connections_list = {}


def receive_message(client_socket: socket.socket):

    try:
        # data = {
        #     "username": "",
        #     "message": ""
        # }

        data = client_socket.recv(1024)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(data):
            return False

        data = data.decode('utf-8')
        print(f"Message data: {data}")
        data = json.loads(data)

        return data
    except:
        # Some error or disconection
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        if notified_socket == sock:
            # Accept new connection
            # That gives us the client socket and the ip/port
            client_socket, client_address = sock.accept()

            # The next message is the client username with the connecting message
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save user
            client_list[client_socket] = user

            # Save connection
            client_connections_list[user["username"]
                                    ] = client_socket.getpeername()

            print(
                f"Accepted new connection from {client_address} with username: {user['username']}")

            # Feature: Send message to all clients about new client connected
            client_socket: socket.socket
            for client_socket in client_list:
                # Send list of servers
                client_connections_list_serialized = json.dumps(
                    client_connections_list)
                client_connections_list_serialized = bytes(
                    client_connections_list_serialized, "utf-8")
                client_socket.send(client_connections_list_serialized)
        else:
            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print(
                    f"Closed connection from: {client_list[notified_socket]['username']}")
                # Feature: Send message to all clients about client disconnected
                client_socket: socket.socket
                for client_socket in client_list:

                    # But don't sent it to sender
                    if client_socket != notified_socket:
                        data = {
                            "username": user['username'],
                            "message": "Left the chat!"
                        }
                        data = json.dumps(data)
                        data = bytes(data, "utf-8")
                        client_socket.send(data)

                # Remove from client_connection_list
                try:
                    del client_connections_list[user["username"]]
                except:
                    # Nothing on the list
                    client_connections_list = {}
                    pass
                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del client_list[notified_socket]

                continue

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del client_list[notified_socket]
