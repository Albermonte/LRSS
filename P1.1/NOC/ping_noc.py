# ping_noc.py

import sys
import socket
import signal
import time

# Comprobamos que haya el número de parámetros requerido
if len(sys.argv) < 3:
    print("Missing params.\n")
    quit()

# Comprobamos que el puerto sea un número, si no lo hacemos produciría un error
if not sys.argv[2].isnumeric():
    print(
        f"Port \"{sys.argv[2]}\" not numeric, usage: python3 ping_noc.py host port\n")
    quit()

HOST = sys.argv[1]
PORT = int(sys.argv[2])
# Definimos el número de mensajes a mandar para poder cambiarlo fácilmente
MSG_AMOUNT = 3


print(f"Running client on {HOST}:{PORT}\n")
# Creamos el socket UDP usando SOCK_DGRAM
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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
    # Guardamos el tiempo actual
    start = time.perf_counter_ns()
    # Enviamos el paquete udp al servidor
    sock.sendto(msg, (HOST, PORT))
    # Quedamos a la espera de la respuesta desde el servidor
    data = sock.recvfrom(1024)
    # Si no recibimos nada, salimos del bucle
    if not data:
        break
    # Guardamos el tiempo actual, otra vez
    end = time.perf_counter_ns()
    # Cálculos para obtener los ms que ha pasado desde que enviamos hasta que recibimos el paquete
    elapsed_ms = (end - start)/1e6
    total_time += elapsed_ms
    print(f"...ping {i} finished, took {elapsed_ms} ms")
    i += 1

# Cálculos finales para mostrar al usuario algunas estadísticas extra
print(
    f"\n## Total Time for {i} pings: {total_time} ms, Mean: {total_time / i} ms ##\n\n")

# Finalmente cerramos el socket
sock.close()
