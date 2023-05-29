import argparse
import datetime
from multiprocessing.pool import ThreadPool
import socket
from NTPPacket import NTPPacket

datetime1900 = datetime.datetime(1900, 1, 1, 5)
reliableSntpServ = "40.119.148.38"
STOP = False


def wait_for_stop():
    while input() != 'stop':
        pass
    global STOP
    STOP = True
    raise Exception('Manual stop')


def try_get_real_time_packet(packet_to_reliable_serv):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(1)
    client.sendto(packet_to_reliable_serv, (reliableSntpServ, 123))
    try:
        data, address = client.recvfrom(1024)
        print("\t[INFO] Real time got success")
        return data
    except:
        print("\t[WARNING] Can not get reliable real time")
        return None


def create_and_send_answer(input_packet, addr, delta, serv):
    receive_time = datetime.datetime.now()
    time_packet = try_get_real_time_packet(input_packet)
    if time_packet is not None:
        packet = NTPPacket().unpack(time_packet)
        packet.stratum = 2
        packet.receive += delta
        packet.transmit += delta + (datetime.datetime.now() - receive_time).total_seconds()
    else:
        packet = NTPPacket().unpack(input_packet)
        packet.mode = 4
        packet.ref_id = 2130706433
        packet.precision = -23
        packet.stratum = 16
        # packet.stratum = 3
        packet.reference = packet.originate
        packet.originate = 0
        packet.receive = (receive_time - datetime1900).total_seconds() + delta
        packet.transmit = (datetime.datetime.now() - datetime1900).total_seconds() + delta

    serv.sendto(packet.pack(), addr)


def net_listener(s, pool, host, port, delay):
    while True:
        data, addr = s.recvfrom(1024)
        print(f'\n{addr} accept to {host}:{port}')
        pool.apply_async(create_and_send_answer, args=(data, addr, delay, s))


def fake_sntp_server(delay: int, port: int):
    host = '127.0.0.1'
    pool = ThreadPool()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print('Fake sntp server started success')
    pool.apply_async(wait_for_stop)
    pool.apply_async(net_listener, args=(s, pool, host, port, delay))
    while not STOP:
        pass
    print("Sntp server stopped")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("delay", help="Разница в секундах от настоящего времени (+- значение)", type=int, default=0)
    parser.add_argument("-p", "--port", help="Порт, который слушаем", type=int, default=124)
    args = parser.parse_args()

    fake_sntp_server(args.delay, args.port)
