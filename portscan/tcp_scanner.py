import socket
from port_result import PortResult


def scan_port(ip: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = PortResult(ip, port)
    result.type = "tcp"
    result.set_open() if s.connect_ex((ip, port)) == 0 else result.set_close()
    s.close()
    return result

