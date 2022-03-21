import errno
import signal
import sys
import select
import socket
import json

def delete_last_line():
    #cursor up one line
    # sys.stdout.write('\x1b[1A')
    #delete last line
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

username = input("Enter your username: ")
if not username:
    username = "Anonymous"
print(f"You choosed {username} as username \n\n")

data = {
    "username": username,
    "message": "connecting"
}
data_send = json.dumps(data)
data_send = bytes(data_send, "utf-8")

sock.send(data_send)

print("###### Connected ######\n\n")
print("You > ", end="", flush=True)


while True:
    # Feature: Non blocking input, receive messages while typing
    is_input, o, e = select.select([sys.stdin], [], [], 0) 

    if is_input:
        message = sys.stdin.readline().strip()

        if message:
            data["message"] = message
            # print(f"Sending {data}")
            data_send = json.dumps(data)
            data_send = bytes(data_send, "utf-8")
            sock.send(data_send)
            print("You > ", end="", flush=True)

    try:
        while True:
            data_received = sock.recv(1024)
            if not len(data_received):
                print("Connection lost")
                sig_handler(0, 0)

            data_received = data_received.decode('utf-8')
            data_received = json.loads(data_received)
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
