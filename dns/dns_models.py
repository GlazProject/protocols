import struct
from dns_utils import byte_at
from dataclasses import dataclass

DNS_RECORD_TYPES = {1: 'a', 2: 'ns', 5: 'cname', 6: 'soa', 12: 'ptr', 15: 'mx', 16: 'txt', 28: 'aaaa'}


class DnsQuery:
    def __init__(self, qname: str, qtype: int, qclass: int):
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass

    def to_bytes(self):
        name = qname2bytes(self.qname)
        bytes_query = struct.pack("!" + str(len(name)) + 's2h', name, self.qtype, self.qclass)
        return bytes_query


@dataclass
class DnsResourceRecord:
    name: str
    rtype: int
    rclass: int
    ttl: int
    rd_length: int
    rdata: bytes

    def to_bytes(self):
        name = qname2bytes(self.name)
        return struct.pack(f'!{len(name)}s2hIH{self.rd_length}s',
                           name, self.rtype, self.rclass, self.ttl, self.rd_length, self.rdata)


@dataclass
class DnsHeader:
    id: int
    qr: bool = True  # is Response
    opcode: int = 0  # request type
    aa: bool = True  # authoritative response
    tc: bool = False  # nat all information in package
    rd: bool = True  # say only ip address
    ra: bool = True  # recursive is available
    rcode: int = 0  # response result code (0 - ok, 1 - invalid format, 2 - internal error, 3 - no name, 4 - unavailable request)
    qd_count: int = 0  # queries request count
    an_count: int = 0  # queries response count
    ns_count: int = 0  # Authority Section count
    ar_count: int = 0  # Additional Record Section count

    def to_bytes(self):
        flags = (self.qr << 15 | (self.opcode & 0b1111) << 11 |
                 self.aa << 10 | self.tc << 9 | self.rd << 8 |
                 self.ra << 7 | (self.rcode & 0b1111))

        return struct.pack('!6H', self.id, flags, self.qd_count,
                           self.an_count, self.ns_count, self.ar_count)

    @staticmethod
    def from_bytes(header_bytes: bytes):
        response_id, flags, qd_count, an_count, ns_count, ar_count = struct.unpack('!6H', header_bytes)

        return DnsHeader(
            id=response_id,
            qr=byte_at(flags, 0, 1) == 1,
            opcode=byte_at(flags, 1, 4),
            aa=byte_at(flags, 5, 1) == 1,
            tc=byte_at(flags, 6, 1) == 1,
            rd=byte_at(flags, 7, 1) == 1,
            ra=byte_at(flags, 8, 1) == 1,
            rcode=byte_at(flags, 12, 4),
            qd_count=qd_count,
            an_count=an_count,
            ns_count=ns_count,
            ar_count=ar_count)


class DnsPackage:
    def __init__(self, header: DnsHeader):
        self.header = header
        self.queries: list[DnsQuery] = []
        self.ans_records: list[DnsResourceRecord] = []
        self.auth_records: list[DnsResourceRecord] = []
        self.additional_records: list[DnsResourceRecord] = []

    def with_queries(self, queries: list[DnsQuery]):
        self.queries = queries
        self.header.qd_count = len(queries)
        return self

    def with_ans_records(self, records: list[DnsResourceRecord]):
        self.ans_records = records
        self.header.an_count = len(records)
        return self

    def with_auth_records(self, records):
        self.auth_records = records
        self.header.ns_count = len(records)
        return self

    def with_additional_records(self, records):
        self.additional_records = records
        self.header.ar_count = len(records)
        return self

    def with_records_from_header(self, records):
        self.with_ans_records(records[:self.header.an_count])
        self.with_auth_records(records[self.header.an_count:self.header.an_count + self.header.ns_count])
        self.with_additional_records(records[self.header.an_count + self.header.ns_count:
                                             self.header.an_count + self.header.ns_count + self.header.ar_count])
        return self

    def to_bytes(self) -> bytes:
        struct_format = '!12s'
        values = [self.header.to_bytes()]
        for p in self.queries + self.ans_records + self.auth_records + self.additional_records:
            part_bytes = p.to_bytes()
            struct_format += str(len(part_bytes)) + 's'
            values.append(part_bytes)
        return struct.pack(struct_format, *values)


def dns_package_with_internal_error(request_id: int, queries):
    header = DnsHeader(request_id, qr=False, aa=False, rcode=2)
    return DnsPackage(header).with_queries(queries)


def qname2bytes(qname: str):
    data = []
    struct_format = '!'
    labels = qname.split('.')
    if labels[-1] == '':
        labels = labels[:-1]
    for label in labels:
        data.append(bytes([len(label)]))
        data.append(label.encode())
        struct_format += 'c' + str(len(label)) + 's'

    data.append(b'\0')
    struct_format += 'c'

    return struct.pack(struct_format, *data)