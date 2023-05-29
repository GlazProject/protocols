import pickle
import time
from datetime import datetime as date
from multiprocessing import Process, Lock

T1970 = date(1970, 1, 1)


def in_seconds(time: date):
    return int((time - T1970).total_seconds())


def seconds_now():
    return in_seconds(date.now())


class DnsCache:
    def __init__(self, cache=None):
        self.locker = Lock()
        self.cache: dict[(str, int, int), dict[bytes, (int, int)]] = {} if cache is None else cache
        # {
        #     'name, type, class':[
        #          {
        #              b'192.168.0.1': {
        #                  ('cached_time': seconds since 1970
        #                  'ttl': seconds)
        #               }
        #          }
        #      ]
        # }

    def get(self, qname: str, qtype: int, qclass: int):
        with self.locker:
            result = []
            key = (qname, qtype, qclass)
            now = seconds_now()
            if key not in self.cache:
                return []
            for data in self.cache[key]:
                cached_time, ttl = self.cache[key][data]
                ttl -= now - cached_time
                if ttl > 0:
                    result.append((data, ttl))
            return result

    def put(self, rname: str, rtype: int, rclass: int, ttl: int, data: bytes):
        with self.locker:
            key = (rname, rtype, rclass)
            value = (seconds_now(), ttl)
            if key not in self.cache:
                self.cache[key] = {}
            self.cache[key][data] = value

    def remove_outdated(self):
        to_remove_keys = []
        with self.locker:
            for key in self.cache:
                to_remove_records = []
                now = seconds_now()
                for data in self.cache[key]:
                    cached_time, ttl = self.cache[key][data]
                    if now - cached_time > ttl:
                        to_remove_records.append(data)

                for record in to_remove_records:
                    self.cache[key].pop(record)
                if len(self.cache[key]) == 0:
                    to_remove_keys.append(key)
            for key in to_remove_keys:
                self.cache.pop(key)


class DnsCacheController:
    def __init__(self, name='dns_cache.bin'):
        self.cache: DnsCache
        self.filename = name
        self.gc = Process(target=self.cache_gc, daemon=True)

    def __enter__(self):
        if not self.load_cache():
            self.cache = DnsCache()
        self.gc.start()
        return self

    def __exit__(self, type, value, traceback):
        self.save_cache()

    def load_cache(self):
        print(f'Начата загрузка кеша из файла {self.filename}')
        try:
            with open(self.filename, 'rb') as file:
                loaded_cache = pickle.load(file)
                self.cache = DnsCache(loaded_cache)
            print(f'Успешно загружено {len(self.cache.cache)} записей')
            return True
        except:
            print('Не удалось загрузить dns кеш')
            return False

    def save_cache(self):
        print(f'Начато сохранение кеша в файл {self.filename}')
        try:
            with open(self.filename, 'wb') as file:
                pickle.dump(self.cache.cache, file)
            print(f'Кеш успешно сохранён')
        except:
            print('Не удалось сохранить dns кеш')

    def cache_gc(self):
        while True:
            self.cache.remove_outdated()
            time.sleep(10)
