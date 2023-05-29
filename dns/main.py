import argparse

from dns_cache import DnsCacheController
from dns_server import DnsCacheServer


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--forwarder', type=str, default='8.8.8.8')
    parser.add_argument('-p', '--port', type=int, default=53)
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()
        with DnsCacheController() as controller:
            DnsCacheServer('127.0.0.1', 53, controller.cache, args.forwarder, args.port).start()
    except:
        print('Что-то пошло не так. Попробуйте запустить от имени администратора')
