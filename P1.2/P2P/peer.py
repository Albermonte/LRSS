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

print(f"Running client on {HOST}:{PORT}\n")

# Connect to server
# Receive list of clients
# Connect to every client

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
# Set recv to not blocking so we can do things while waiting for msg
sock.setblocking(False)


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

    try:
        while True:
            data_received = sock.recv(1024)
            # The server was closed
            if not len(data_received):
                print("Connection lost")
                sig_handler(0, 0)

            # Convert string to json
            data_received = data_received.decode('utf-8')
            data_received = json.loads(data_received)
            print(data_received)
            try:
                a = data_received["username"]
                pass
            except:
                del data_received[username]
                client_connections_list = data_received
                for client_name in client_connections_list:
                    conn = client_connections_list[client_name]
                    ip = conn[0]
                    port = conn[1]
                    print("Listening...")
                    # server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # server_sock.bind()
                    # server_sock.listen()
                    # TODO: bind to sport?
                    # new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # new_sock.connect((ip, port))
                    data = {
                        "username": username,
                        "message": "Hola"
                    }
                    # Convert to json and send
                    data_send = json.dumps(data)
                    data_send = bytes(data_send, "utf-8")
                    sock.sendto(data_send, (ip, port))
                    # Connect to other sockets
                    # Save in sockets_list
                    # Do the same as server did

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print(f"Reading error: {str(e)}")
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print(f"Reading error: {str(e)}")
        sig_handler(0, 0)

# Source: https://github.com/engineer-man/youtube/blob/master/141/client.py
