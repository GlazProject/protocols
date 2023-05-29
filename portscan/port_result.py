

class PortResult:
    def __init__(self, host: str, port: int, is_open: bool = False):
        self.host = host
        self.port = port
        self.is_open = is_open
        self.type = ""
        self.description = ""

    def set_open(self):
        self.is_open = True
        return self

    def set_close(self):
        self.is_open = False
        return self

    def to_string(self):
        return f'{"" if self.is_open else "close"} {self.port}/{self.type}: {self.description}'
