from dataclasses import dataclass


def empty():
    return SmtpAnswer('', '0', '')


def from_str(msg: str):
    msg = msg.strip()
    if msg == '':
        return empty()
    last_line = msg.split('\n')[-1]
    return SmtpAnswer(msg, last_line[0:4], last_line[5:])


@dataclass
class SmtpAnswer:
    answer: str
    code: str
    message: str

    def __str__(self):
        return self.answer

    def has_error(self):
        return self.code.startswith('5') or self.code.startswith('4')
