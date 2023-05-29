import argparse
import re
import socket
import handmade_tracer.inet as tracer

from IpEntry import IpEntry


def run_whois(server: str, query: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, 43))

    s.send((bytes(query, 'utf-8')) + b'\r\n')
    msg = ''
    while len(msg) < 10000:
        try:
            receive_data = str((s.recv(100)), encoding='utf-8')
            if receive_data == '':
                break
            msg = msg + receive_data
        except:
            pass
    s.close()
    return msg


def get_whois_data_(ip: str, whois: str = 'whois.iana.org', is_main = True):
    servs = ("whois.arin.net", "whois.lacnic.net", "whois.ripe.net", "whois.afrinic.net", "whois.apnic.net")
    
    msg = run_whois(whois, ip)
    net_name = ""
    country = ""
    as_number = ""
    for line in msg.splitlines():
        if line.startswith("whois"):
            return get_whois_data_(ip, line.split(':')[1].strip(), False)
        if re.match(re.compile(r"^[Nn]et[Nn]ame"), line) is not None:
            net_name = line.split(':')[1].strip()
        if re.match(re.compile(r"^[Cc]ountry"), line) is not None:
            country = line.split(':')[1].strip()
        if line.startswith("origin") or line.startswith("OriginAS"):
            as_number = line.split(':')[1].strip()

    if is_main and net_name=="" and country == "" and as_number=="":
        for s in servs:
            n_name, n_country, n_number = get_whois_data_(ip, s, False)
            net_name = net_name if n_name == "" else n_name
            country = country if n_country == "" else n_country
            as_number = as_number if n_number == "" else n_number

    return net_name, country, as_number
    


def is_local(ip):
        segments = [int(x) for x in ip.split('.')]

        # 10.0.0.0 — 10.255.255.255
        if segments[0] == 10:
            return True
        # 192.168.0.0 — 192.168.255.255
        if segments[0] == 192 and segments[1] == 168:
            return True
        # 100.64.0.0 — 100.127.255.255
        if segments[0] == 100 and 127 >= segments[1] >= 64:
            return True
        # 172.16.0.0 — 172.31.255.255
        if segments[0] == 172 and 31 >= segments[1] >= 16:
            return True
        return False


def fill_traceroute(entries):
    for entry in entries:
        net_name, country, as_number = get_whois_data_(entry.ip)
        if net_name != "":
            entry.net_name = net_name
        if country != "":
            entry.country = country
        if as_number != "":
            entry.as_number = as_number
        yield entry
    

def get_ip_entries(ip: str, hops: int):
    number = 1
    for e in tracer.run(ip, 1, hops):
        node, t, v = e
        entry = IpEntry(number, node)
        number += 1
        yield entry
        if t == 0:
            return
        if number == hops:
            print("Превышено чило промежуточных узлов")
            return


def get_traceroute(host: str, hops: int):
    ip = socket.gethostbyname(host)
    print(f"Start trace to {host} [{ip}] with max ttl={hops}")
    if (is_local(ip)):
        print("Локальные адреса не маршрутизируются")
        return ()
    trace = get_ip_entries(ip, hops)
    return fill_traceroute(trace)


def print_traceroute(trace):
    for entry in trace:
        print(entry.__str__())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="url или ip ресурса, до которого необходимо построить путь")
    parser.add_argument("--max_hops", help="Максимальное количество промежуточных узлов", type=int, default=30)
    args = parser.parse_args()

    try:
        route = get_traceroute(args.ip, args.max_hops)
        print_traceroute(route)
    except:
        print("Случилась непредвиденная ошибка. \r\nПожалуйста, проверьте данные и повторите попытку от имени администратора")
