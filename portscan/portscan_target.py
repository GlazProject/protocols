import socket
from multiprocessing.pool import ThreadPool


def listen(port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", port))
    s.listen()
    while True:
        connection, client_address = s.accept()
        try:
            print(f'{port}: connection from', client_address)
        finally:
            connection.close()


def start_listen(ports: list[int]):
    pool = ThreadPool()
    for port in ports:
        pool.apply_async(listen, args=[port])
    print("Start listening")

    while input() != "stop":
        pass


if __name__ == '__main__':
    start_listen(list(map(int, input().split())))
