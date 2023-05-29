class IpEntry:
    def __init__(self, number: int, ip: str):
        self.number = number
        self.ip = ip
        self.net_name = ""
        self.as_number = ""
        self.country = ""

    def __str__(self):
        result = f"{self.number}. {self.ip}\r\n"
        if self.ip == "*":
            return result

        if self._is_local():
            result += "local\r\n"
            return result

        data = []
        if self.net_name != "":
            data.append(self.net_name)
        if self.as_number != "":
            data.append(self.as_number[2:])
        if self.country != "" and self.country != "EU":
            data.append(self.country)

        return result + ", ".join(data) + "\r\n"

    def _is_local(self):
        segments = [int(x) for x in self.ip.split('.')]

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

