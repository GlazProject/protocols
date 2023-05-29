import struct
import time


def get_fraction(number, precision):
    return int((number - int(number)) * 2 ** precision)


class NTPPacket:
    # ! - network byte order (big-endian)
    # B - unsigned char (integer) 1 byte
    # b - signed char (integer) 1 bytes
    # 11 - count of I symbols
    # I - unsigned int (integer) 4 bytes
    _FORMAT = "!BBbb11I"

    def __init__(self, version_number=2, mode=3):
        self.leap_indicator = 0  # 2 bits
        self.version_number = version_number  # 3 bits
        self.mode = mode  # 3 bits
        self.stratum = 0  # 1 byte
        self.pool = 0  # 1 byte
        self.precision = 0  # 1 byte
        self.root_delay = 0  # 4 byte
        self.root_dispersion = 0  # 4 byte
        self.ref_id = 0  # 4 byte
        self.reference = 0  # 8 byte
        self.originate = 0  # 8 byte
        self.receive = 0  # 8 byte
        self.transmit = 0  # 8 byte

    def pack(self):
        return struct.pack(NTPPacket._FORMAT,
                           (self.leap_indicator << 6) +
                           (self.version_number << 3) + self.mode,
                           self.stratum,
                           self.pool,
                           self.precision,
                           int(self.root_delay) + get_fraction(self.root_delay, 16),
                           int(self.root_dispersion) +
                           get_fraction(self.root_dispersion, 16),
                           int(self.ref_id),
                           int(self.reference),
                           get_fraction(self.reference, 32),
                           int(self.originate),
                           get_fraction(self.originate, 32),
                           int(self.receive),
                           get_fraction(self.receive, 32),
                           int(self.transmit),
                           get_fraction(self.transmit, 32))

    def unpack(self, data: bytes):
        unpacked_data = struct.unpack(NTPPacket._FORMAT, data)

        self.leap_indicator = unpacked_data[0] >> 6  # 2 bits
        self.version_number = unpacked_data[0] >> 3 & 0b111  # 3 bits
        self.mode = unpacked_data[0] & 0b111  # 3 bits

        self.stratum = unpacked_data[1]  # 1 byte
        self.pool = unpacked_data[2]  # 1 byte
        self.precision = unpacked_data[3]  # 1 byte

        # 2 bytes | 2 bytes
        self.root_delay = (unpacked_data[4] >> 16) + \
                          (unpacked_data[4] & 0xFFFF) / 2 ** 16
        # 2 bytes | 2 bytes
        self.root_dispersion = (unpacked_data[5] >> 16) + \
                               (unpacked_data[5] & 0xFFFF) / 2 ** 16

        # 4 bytes
        self.ref_id = unpacked_data[6]

        self.reference = unpacked_data[7] + unpacked_data[8] / 2 ** 32  # 8 bytes
        self.originate = unpacked_data[9] + unpacked_data[10] / 2 ** 32  # 8 bytes
        self.receive = unpacked_data[11] + unpacked_data[12] / 2 ** 32  # 8 bytes
        self.transmit = unpacked_data[13] + unpacked_data[14] / 2 ** 32  # 8 bytes

        return self

    def to_display(self):
        return f"Leap indicator: {self.leap_indicator}\n" \
               f"Version number: {self.version_number}\n" \
               f"Mode: {self.mode}\n" \
               f"Stratum: {self.stratum}\n" \
               f"Pool: {self.pool}\n" \
               f"Precision: {self.precision}\n" \
               f"Root delay: {self.root_delay}\n" \
               f"Root dispersion: {self.root_dispersion}\n" \
               f"Ref id: {self.ref_id}\n" \
               f"Reference: {self.reference}\n" \
               f"Reference as time: {time.ctime(self.reference)}\n" \
               f"Originate: {self.originate}\n" \
               f"Originate as time: {time.ctime(self.originate)}\n" \
               f"Receive: {self.receive}\n" \
               f"Receive as time: {time.ctime(self.receive)}\n" \
               f"Transmit: {self.transmit}\n" \
               f"Transmit as time: {time.ctime(self.transmit)}"
