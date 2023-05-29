import socket
from portscan.port_result import PortResult


def scan_port(ip: str, port: int) -> PortResult:
    result = PortResult(ip, port)
    result.type = 'udp'
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1)
        try:
            sock.sendto(b'ping', (ip, port))
            data, _ = sock.recvfrom(1024)
            # ICMP (3,3) response = closed
            if data.startswith(bytes([3, 3])):
                return result.set_close()
        except socket.timeout:
            return result.set_open()
        except socket.error:
            return result.set_close()
