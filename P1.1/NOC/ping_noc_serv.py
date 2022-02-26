import sys
import signal
import socket

if len(sys.argv) < 2:
    print("Missing param PORT.\n")
    quit()

PORT = int(sys.argv[1])
print(f"Running server on Port: {PORT}")

print("Creating Socket")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

print("Binding address and port")
server_address = ('localhost', PORT)
sock.bind(server_address)

# while True so server is not stopped when client disconnected
while True:
    print("Waiting for connection")
    data, client_address = sock.recvfrom(1024)

    if data:
        print(f"Receiving data from {client_address}... Sending back")
        sock.sendto(data, client_address)
