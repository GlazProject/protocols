import socket
from multiprocessing import Process
from multiprocessing.pool import ThreadPool
from threading import Thread

from dns_cache import DnsCache
from dns_models import DnsPackage, dns_package_with_internal_error, DnsHeader, DnsResourceRecord, DNS_RECORD_TYPES
from dns_parser import bytes2package


def _resolve_host(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except Exception as e:
        raise DnsCacheServerException(f'Can not resolve host "{host}"', e)


class DnsCacheServer:
    def __init__(self, host: str, port: int, cache: DnsCache, fw_host: str, fw_port: int = 53):
        self.host = host
        self.port = port
        self.fw_address = (_resolve_host(fw_host), fw_port)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.cache: DnsCache = cache
        self.pool = ThreadPool()
        self.dns_demon = Thread(target=self.run, daemon=True)
        self.active = True

    def stop_listener(self):
        while input() != 'stop':
            pass
        self.active = False
        self.dns_demon.join(0)
        print('DNS сервер остановлен')

    def run(self):
        print('DNS сервер успешно запущен')

        while True:
            if not self.active:
                break
            try:
                request_bytes, address = self.server_sock.recvfrom(512)
                self.start_answer(request_bytes, address)
                # self.pool.apply_async(self.start_answer, args=(request_bytes, address))
            except:
                pass

    def start(self):
        reverse_host = self.host.split('.')
        reverse_host.reverse()
        arpa_name = '.'.join(reverse_host + ['in-addr.arpa'])
        self.cache.put(arpa_name, 12, 1, 9999, b'Personal cache dns server')
        self.server_sock.bind((self.host, self.port))
        self.dns_demon.start()
        self.stop_listener()

    def start_answer(self, request_bytes: bytes, address: tuple[str, int]):
        request = bytes2package(request_bytes)
        for q in request.queries:
            print(f'\nЗапрос от {address}: {q.qname} type {DNS_RECORD_TYPES[q.qtype] if q.qtype in DNS_RECORD_TYPES else q.qtype}')

        dns_response = self.from_cache(request)
        if dns_response == b'':
            dns_response = self.from_forwarder(request, request_bytes)

        self.server_sock.sendto(dns_response, address)
        print(f'\t[{request.header.id}] Отправлено {address}')

    def from_forwarder(self, dns_request: DnsPackage, request_bytes: bytes) -> bytes:
        print(f'\t[{dns_request.header.id}] Не найдены кешированные записи. Обращение к {self.fw_address}...')
        try:
            if (self.host, self.port) == self.fw_address:
                print(f'\t[{dns_request.header.id}] Вышестоящий сервер образует петлю. Запрос отклонён')
                raise DnsCacheServerException(f'[{dns_request.header.id}] Cyclic DNS request')

            fw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            fw_sock.settimeout(5)
            fw_sock.sendto(request_bytes, self.fw_address)
            response_bytes, _ = fw_sock.recvfrom(512)

            print(f'\t[{dns_request.header.id}] Получен ответ от {self.fw_address}')
            dns_response = bytes2package(response_bytes)

            for r in dns_response.ans_records + dns_response.auth_records + dns_response.additional_records:
                self.cache.put(r.name, r.rtype, r.rclass, r.ttl, r.rdata)
            return response_bytes

        except:
            print(f'\t[{dns_request.header.id}] Вышестоящий сервер недоступен')
            return dns_package_with_internal_error(dns_request.header.id, dns_request.queries).to_bytes()

    def from_cache(self, dns_request: DnsPackage) -> bytes:
        ans_records = []
        for q in dns_request.queries:
            for data, ttl in self.cache.get(q.qname, q.qtype, q.qclass):
                if len(data) == 0:
                    continue
                ans_records.append(DnsResourceRecord(q.qname, q.qtype, q.qclass, ttl, len(data), data))
        if len(ans_records) == 0:
            return b''
        print(f'\t[{dns_request.header.id}] Найдено в кеше')
        header = DnsHeader(dns_request.header.id, aa=False)
        response = DnsPackage(header)
        response.with_queries(dns_request.queries).with_ans_records(ans_records)
        return response.to_bytes()


class DnsCacheServerException(Exception):
    def __init__(self, msg: str = None, inner_exception: Exception = None):
        self.msg = msg
        self.inner_exception = inner_exception
