import argparse
import socket
from multiprocessing.pool import ThreadPool

import tcp_scanner
import udp_scanner
from port_result import PortResult
from utils import recognise_port, RESULTS, GREEN, DEFAULT, start_printer


def scan_port_and_save_if_open(ip: str, port: int, out: list[PortResult], scanner):
    result = scanner.scan_port(ip, port)
    if result.is_open:
        out.append(recognise_port(result))
        RESULTS.append(GREEN + result.to_string() + DEFAULT)


def find_open_ports(ip: str, port_from: int, port_to_including: int, scanner) -> list[PortResult]:
    pool = ThreadPool()
    ports = []
    for port in range(port_from, port_to_including + 1):
        pool.apply_async(scan_port_and_save_if_open, args=(ip, port, ports, scanner))

    pool.close()
    pool.join()
    return ports


def main(host: str, port_from: int, port_to: int, tcp: bool, udp: bool):
    try:
        ip = socket.gethostbyname(host)
    except socket.error:
        print("\033[31m" + f"Введённый хост \"{host}\" не найден. Проверьте корректность и повторите попытку"
              + "\033[0m")
        return

    if not tcp and not udp:
        print("Не указан тип сканирования. Используйте --help для подробностей")
        return

    print("\033[36m" + f"\nЗапуск сканирования {host} [{ip}]" + "\033[0m")
    start_printer()

    if tcp:
        print("\033[36m" + f"\ntcp сканирование запущено c {port_from} по {port_to} порты" + "\033[0m")
        print("\tСканирование может занять некоторое время, пожалуйста, ожидайте завершения")
        find_open_ports(ip, port_from, port_to, tcp_scanner)

    if udp:
        print("\033[36m" + f"\nudp сканирование запущено c {port_from} по {port_to} порты" + "\033[0m")
        print("\tСканирование может занять некоторое время, пожалуйста, ожидайте завершения")
        find_open_ports(ip, port_from, port_to, udp_scanner)

    print("\033[36m" + "\nСканирование завершено" + "\033[0m")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="IP адрес или host, у которого необходимо просканировать порты", type=str)
    parser.add_argument("-t", help="TCP сканирование", action="store_true", default=False)
    parser.add_argument("-u", help="UDP сканирование", action="store_true", default=False)
    parser.add_argument("-p", "--ports", help="Диапазон портов сканирования (включительно)", type=int,
                        default=[1, 1024], nargs=2)

    args = parser.parse_args()

    main(args.host, args.ports[0], args.ports[1], args.t, args.u)
