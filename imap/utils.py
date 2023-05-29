import base64
import quopri
import re

DEFAULT = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CIAN = "\033[96m"
YELLOW = "\033[93m"


class ImapServerException(Exception):
    def __init__(self, msg):
        self.msg = msg


def decode_base64_string(data: str, encode_to: str):
    return base64.b64decode(data.encode()).decode(encode_to)


def decode_qbyte_string(data: str, encode_to: str):
    return quopri.decodestring(data.encode()).decode(encode_to)


def get_headers(answer: str):
    from_re = r'(From):((\s.+\n)+)'
    to_re = r'(To):((\s.+\n)+)'
    subject_re = r'(Subject):((\s.+\n)+)'
    date_re = r'(Date): (.+)'
    res = [from_re, to_re, subject_re, date_re]
    result = {}

    for r in res:
        matches = re.finditer(r, answer, re.MULTILINE)
        for match in matches:
            value = match.group(2).replace('\r\n ', '').replace('?= =?', '?==?').strip()
            decoded = decode_data(value)
            if len(decoded) > 0:
                result[match.group(1)] = decoded

    regex = r"\(\"[^\"]+\" \"[^\"]+\" \(\"name\" \"[^\"]+\"\)[^(]+ (\d+) " \
            r"[^(]+\(\"attachment\" \(\"filename\" \"([^\"]+)\"\)\)"
    matches = re.finditer(regex, answer, re.MULTILINE)
    attachments = [(decode_data(match.group(2)), match.group(1)) for match in matches]
    if len(attachments) != 0:
        result['Attachments'] = attachments

    return result


def print_headers(headers: dict[str, str]):
    print(CIAN + '-' * 10 + DEFAULT)
    if "From" in headers:
        print(f"{YELLOW}От: {DEFAULT}" + headers["From"])
    if "To" in headers:
        print(f'{YELLOW}Кому: {DEFAULT}' + headers["To"])
    if "Date" in headers:
        print(f'{YELLOW}Дата: {DEFAULT}' + headers["Date"])
    if "Subject" in headers:
        print(f'{YELLOW}Тема: {DEFAULT}' + headers["Subject"])
    if "Attachments" in headers:
        print(f'{YELLOW}Вложения: {DEFAULT}')
        for name, size in headers['Attachments']:
            print(f'{" "*10}{name} ({(int(size) / 1.33) // 1024} кБайт)')
    print(CIAN + '-' * 10 + DEFAULT)


def decode_data(data: str):
    regex = r"=\?([^?]+)\?(\w)\?([^?]*)\?="
    matches = re.finditer(regex, data, re.MULTILINE)

    for match in matches:
        encode_to = match.group(1).lower()
        decode_from = match.group(2).lower()
        text = match.group(3)
        if decode_from == 'b':
            text = decode_base64_string(text, encode_to)
        elif decode_from == 'q':
            text = decode_qbyte_string(text, encode_to)

        a = match.group()
        data = data.replace(a, text)

    return data
