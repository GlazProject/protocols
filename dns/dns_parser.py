import struct

from dns_models import DnsQuery, DnsHeader, DnsPackage, DnsResourceRecord


def bytes2package(data: bytes) -> DnsPackage:
    header, queries = struct.unpack(f'!12s{len(data) - 12}s', data)
    header = DnsHeader.from_bytes(header)
    queries, records_bytes = bytes2queries(queries, header.qd_count, data)
    records = bytes2records(records_bytes, data)
    return DnsPackage(header).with_queries(queries).with_records_from_header(records)


def bytes2queries(queries_bytes: bytes, queries_count: int, body: bytes):
    queries = []
    for i in range(queries_count):
        qname, queries_bytes = read_qname(queries_bytes, body)
        qtype = int(struct.unpack('!H', queries_bytes[:2])[0])
        qclass = int(struct.unpack('!H', queries_bytes[2:4])[0])
        queries_bytes = queries_bytes[4:]

        queries.append(DnsQuery(qname, qtype, qclass))
    return queries, queries_bytes


def read_qname(queries_bytes: bytes, body: bytes):
    labels = []
    label_len = queries_bytes[0]
    queries_bytes = queries_bytes[1:]
    while label_len > 0:
        if label_len & 0b1100_0000:
            ptr = (label_len ^ 0b1100_0000) << 8 | queries_bytes[0]
            queries_bytes = queries_bytes[1:]
            domain, _ = read_qname(body[ptr:], body)
            labels.append(domain)
            break
        labels.append(queries_bytes[:label_len].decode())
        queries_bytes = queries_bytes[label_len:]
        label_len = queries_bytes[0]
        queries_bytes = queries_bytes[1:]
    qname = '.'.join(labels)
    return qname, queries_bytes


def bytes2records(records_bytes: bytes, body: bytes):
    records = []
    while len(records_bytes) > 0:
        record, records_bytes = bytes2record(records_bytes, body)
        records.append(record)
    return records


def bytes2record(record_bytes: bytes, body: bytes):
    domain, data = read_qname(record_bytes, body)
    rtype, rclass, ttl, rdlength, data = struct.unpack(f'!2hIH{len(data) - 10}s', data)
    rdata, next_record = struct.unpack(f'!{rdlength}s{len(data) - rdlength}s', data)

    record = DnsResourceRecord(domain, rtype, rclass, ttl, rdlength, rdata)
    return record, next_record
