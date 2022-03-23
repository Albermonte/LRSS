# cliente.py

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
# flush=True to avoid errors, without it this line was not printed
print("You > ", end="", flush=True)


while True:
    # Feature: Non blocking input, receive messages while typing
    is_input, _, _ = select.select([sys.stdin], [], [], 0)

    if is_input:
        message = sys.stdin.readline().strip()

        # If not message (eg: \n) don't send it
        if message:
            # TODO: Check if message + username + data > 1024
            data["message"] = message
            # print(f"Sending {data}")
            data_send = json.dumps(data)
            data_send = bytes(data_send, "utf-8")
            sock.send(data_send)
            print("You > ", end="", flush=True)

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
            # Delete last line and print data, this will replace "You >" with another client message
            delete_last_line()
            print(f"{data_received['username']} : {data_received['message']}")
            print("You > ", end="", flush=True)

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

# Sources:
#  https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
#  https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
#  https://stackoverflow.com/questions/21791621/taking-input-from-sys-stdin-non-blocking
