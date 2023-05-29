import socket
import struct

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'  # white
Y = '\033[33m'  # yellow


def set_icmp_header():
    temp_header = struct.pack("bbHHh", 8, 0, 0, 0, 0)
    checksum = calculate_checksum(temp_header)
    header = struct.pack("bbHHh", 8, 0, checksum, 0, 0)
    return header


def calculate_checksum(packet):
    """
    Calculates checksum according RFC 792

    :param packet:
    :return:
    """
    checksum = 0
    for i in range(0, len(packet), 2):
        word = packet[i] + (packet[i + 1] << 8)
        checksum = checksum + word
        overflow = checksum >> 16
        while overflow > 0:
            checksum = checksum & 0xFFFF
            checksum = checksum + overflow
            overflow = checksum >> 16
    overflow = checksum >> 16
    while overflow > 0:
        checksum = checksum & 0xFFFF
        checksum = checksum + overflow
        overflow = checksum >> 16
    checksum = ~checksum
    checksum = checksum & 0xFFFF
    return checksum


def run(ip: str, timeout: int, max_hops: int):
    r = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    r.settimeout(timeout)

    for ttl in range(1, max_hops):
        r.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        r.sendto(set_icmp_header(), (ip, 1))
        try:
            data = r.recvfrom(1024)[0]
            ip_header = data[0:20]
            # ! - network byte order (big-endian)
            # B - unsigned char (integer) 1 byte
            # H - unsigned short (integer) 2 bytes
            # 4s - 4 byte char[] "string" (byte) 4 bytes
            ip_struct = struct.unpack('!BBHHHBBH4s4s', ip_header)
            yield (socket.inet_ntoa(ip_struct[8]), *struct.unpack('BB', data[20:22]))

            if struct.unpack('BB', data[20:22])[0] == 0:
                return
        except socket.error as e:
            yield ('*', -1, -1)

    r.close()


if __name__ == '__main__':
    run("93.186.225.194", 1, 30)
