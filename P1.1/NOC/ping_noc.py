import sys
import socket
import signal
import time

if len(sys.argv) < 3:
    print("Missing params.\n")
    quit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])
MSG_AMOUNT = 3

print(f"Running client on {HOST}:{PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

i = 0
while i < MSG_AMOUNT:
    print(f"Sending ping {i}...\t", end='')
    start = time.perf_counter_ns()
    sock.sendto(b"a", (HOST, PORT))
    data = sock.recvfrom(1024)
    if not data:
        break
    end = time.perf_counter_ns()
    elapsed_ms = (end - start)/1e6
    print(f"...ping {i} finished, took {elapsed_ms} ms")
    i += 1

sock.close()