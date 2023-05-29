import base64

DEFAULT = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CIAN = "\033[96m"
YELLOW = "\033[93m"


class ServerNameException(Exception):
    def __init__(self, msg):
        self.msg = msg


class SmtpServerException(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_base64_str(data: str):
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")
