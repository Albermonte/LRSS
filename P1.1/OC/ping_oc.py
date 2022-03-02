import signal
import sys
import socket
import time

if len(sys.argv) < 3:
    print("Missing params.\n")
    quit()

if not sys.argv[2].isnumeric():
    print(
        f"Port \"{sys.argv[2]}\" not numeric, usage: python3 ping_oc.py host port\n")
    quit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])
MSG_AMOUNT = 3

print(f"Running client on {HOST}:{PORT}\n")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))


def sig_handler(signum, frame):
    print("\nClosing socket...")
    sock.close()
    quit()


signal.signal(signal.SIGINT, sig_handler)

i = 0
total_time = 0
msg = b"a"

print(
    f"Pinging to {HOST} with a total of {sys.getsizeof(msg) * MSG_AMOUNT} bytes:\n")

while i < MSG_AMOUNT:
    print(f"Sending ping {i} of {sys.getsizeof(msg)} bytes...\t", end='')
    start = time.perf_counter_ns()
    sock.sendall(b"a")
    data = sock.recv(1024)
    if not data:
        break
    end = time.perf_counter_ns()
    elapsed_ms = (end - start)/1e6
    total_time += elapsed_ms
    print(f"...ping {i} finished, took {elapsed_ms} ms")
    i += 1

sock.close()

print(
    f"\n## Total Time for {i} pings: {total_time} ms, Mean: {total_time / i} ms ##\n\n")
