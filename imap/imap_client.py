import socket
import ssl
from getpass import getpass

from utils import ImapServerException, get_headers, print_headers


class ImapClient:
    def __init__(self, user: str, server: str, port: int, use_ssl: bool):
        self.user = user
        self.port = port
        self.server = server
        self.use_ssl = use_ssl
        self.sock: [socket.socket, None] = None
        self.password = getpass(prompt='Пароль для авторизации: ')

    def send(self, message: str):
        if self.sock is None:
            raise ImapServerException("No connection")
        message = message + '\r\n'
        self.sock.send(message.encode("utf-8"))

    def receive(self):
        if self.sock is None:
            raise ImapServerException("No connection")
        response = b''
        while True:
            try:
                string = self.sock.recv(1024)
                response += string
                if len(string) < 1024:
                    break
            except Exception:
                break
        message = response.decode('utf-8')
        if 'BAD' in message or 'NO' in message:
            raise ImapServerException(message)
        while not any([x in message for x in ['BAD', 'NO', 'OK']]):
            message += self.receive()
        return message

    def log_in(self):
        self.send(f'CM0 LOGIN {self.user} {self.password}')
        self.receive()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)

        try:
            print(f'Подключение к серверу {self.server}:{self.port}...')
            self.sock.connect((self.server, self.port))

            if self.use_ssl:
                self.sock = ssl.wrap_socket(self.sock)

            self.receive()
            self.log_in()

        except ImapServerException as e:
            self.sock.close()
            self.sock = None
            raise e
        return self

    def print_message(self, number: int):
        self.send(f'CMD3 FETCH {number} (BODY[HEADER.FIELDS (Date From To Subject)] BODYSTRUCTURE)')
        answer = get_headers(self.receive())
        print_headers(answer)
        print('\n\n')

    def read(self, m_from: int, m_to: int, mailbox: str):
        self.send(f'CMD1 SELECT {mailbox}')
        try:
            msg_count = int(self.receive().split('\n')[1].split(' ')[1]) + 1
        except:
            return
        for i in range(msg_count - m_from, msg_count - m_to - 1, -1):
            self.print_message(i)
        return self

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
