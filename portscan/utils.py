import socket
import threading

from portscan.port_result import PortResult

RESULTS = []
DEFAULT = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"


def print_results():
    while True:
        try:
            print(RESULTS.pop())
        except IndexError:
            pass


def recognise_port(port: PortResult) -> PortResult:
    try:
        port.description = socket.getservbyport(port.port, port.type)
    except socket.error:
        pass
    return port


def start_printer():
    printer = threading.Thread(target=print_results, daemon=True)
    printer.start()
