import datetime
import socket
import time
from NTPPacket import NTPPacket
from multiprocessing.pool import ThreadPool

datetime1970 = datetime.datetime(1970, 1, 1)
TIME70 = (datetime1970 - datetime.datetime(1900,1,1)).total_seconds()


def sntp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    data = NTPPacket()
    originate = (datetime.datetime.now() - datetime1970).total_seconds()
    data.originate = originate
    client.sendto(data.pack(), ('127.0.0.1', 124))

    try:
        data, address = client.recvfrom(1024)
    except:
        print("Can not get answer from sntp server on 127.0.0.1")
        return

    if data:
        print('Response received from:', address)
        packet = NTPPacket().unpack(data)
        if packet.stratum == 16:
            print("\tData is broken")
            print()
            return

        client_delay = (datetime.datetime.now() - datetime1970).total_seconds() - originate
        serv_delay = packet.transmit - packet.receive
        net_delay = (client_delay - serv_delay) / 2
        print(f'\tComputer time:\t{datetime.datetime.now().ctime()}')
        print(f'\tReceived Time:\t{time.ctime(packet.transmit - net_delay - TIME70)}')
        print()

    client.close()


if __name__ == '__main__':
    while input("Отправить запрос? [y/n]: ") == "y":
        sntp_client()
        print()

    # i = 1
    # pool = ThreadPool()
    # for i in range(30):
    #     pool.apply_async(sntp_client, args=[i])
    #     i+=1
    # time.sleep(10)
