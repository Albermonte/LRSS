# servidor.py

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
RECV_BUFFER = 1024

# Socket TCP
# Conect non-blockin
# Listen for msgs from every client
# Send msg to every client except the origin

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


def receive_message(client_socket: socket.socket):

    try:
        # data = {
        #     "username": "",
        #     "message": ""
        # }

        data = client_socket.recv(RECV_BUFFER)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(data):
            return False

        data = data.decode('utf-8')
        print(f"Message data: {data}")
        if not data.startswith("file-"):
            data = json.loads(data)
            return data
        else:
            filename = data.split("file-")[1] + ".temp"
            # It's a file then, could be improved because here we will catch other errors :/
            with open(filename, "wb") as f:
                while True:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = client_socket.recv(RECV_BUFFER)
                    if not bytes_read:
                        # TODO: Not working, not reaching here
                        print("File received")
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
            # TODO: Not working, not reaching here
            print(f"Filename: {filename}")
            return filename

    except Exception as e:
        print("Error receiving msg")
        print(e)
        # Some error or disconection
        return False


while True:
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
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

            print(
                f"Accepted new connection from {client_address} with username: {user['username']}")

            # Feature: Send message to all clients about new client connected
            client_socket: socket.socket
            for client_socket in client_list:
                data = {
                    "username": user['username'],
                    "message": "Entered the chat!"
                }
                data = json.dumps(data)
                data = bytes(data, "utf-8")
                client_socket.send(data)

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)
            print(f"Message: {message}")

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

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del client_list[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = client_list[notified_socket]

            if not type(message) is dict:
                print(
                    f"Received message from {user['username']} : {message['message']}")

            # Iterate over connected clients and broadcast message
            client_socket: socket.socket
            for client_socket in client_list:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    if not type(message) is dict:
                        sock.send(bytes(message, "utf-8"))
                        with open(message, "rb") as f:
                            print(f"Sending file {message}")
                            while True:
                                # Read the bytes from the file
                                bytes_read = f.read(RECV_BUFFER)
                                if not bytes_read:
                                    # file transmitting is done
                                    print("File sent")
                                    break
                                sock.sendall(bytes_read)
                        continue

                    data = {
                        "username": user['username'],
                        "message": message['message']
                    }
                    data = json.dumps(data)
                    data = bytes(data, "utf-8")
                    client_socket.send(data)

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del client_list[notified_socket]


# Sources:
# https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
# https://mirdan.medium.com/send-json-with-python-socket-f1107876f50e
