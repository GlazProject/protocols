import socket
import ssl

import smtp_answer
from getpass import getpass
from utils import DEFAULT, RED, GREEN, CIAN, YELLOW, SmtpServerException, get_base64_str


class SmtpClient:
    def __init__(self,
                 addr_from: str, addr_to: str, server: str, port: int,
                 use_ssl: bool, need_auth: bool, print_log: bool):
        self.addr_from = addr_from
        self.addr_to = addr_to
        self.use_ssl = use_ssl
        self.need_auth = need_auth
        self.print_log = print_log
        self.server = server
        self.port = port
        self.sock: [socket.socket, None] = None

        if self.need_auth:
            self.password = getpass(prompt='Пароль для авторизации: ')

    def print(self, message: str):
        if self.print_log:
            print(message)

    def print_success(self, message: str):
        self.print(GREEN + message + DEFAULT)

    def log_from_server(self, message: str):
        self.print(f'{YELLOW}<--- SMTP Server:{DEFAULT} {message}')

    def log_from_client(self, message: str):
        self.print(f'{CIAN}SMTP Client --->{DEFAULT}: {message}')

    def host_name(self):
        return self.addr_from.replace("@", ".")

    def create_init_commands(self):
        yield f'EHLO {self.host_name()}\n'
        if self.need_auth:
            yield 'auth login\n'
            yield f'{get_base64_str(self.addr_from)}\n'
            yield f'{get_base64_str(self.password)}\n'
        yield f'MAIL FROM: <{self.addr_from}>\n' \
              f'RCPT TO: <{self.addr_to}>\n' \
              f'DATA\n'

    def start_ssl(self):
        self.send(f'EHLO {self.host_name()}\n')
        self.receive()
        self.send('starttls\n')
        self.receive()
        return ssl.wrap_socket(self.sock)

    def send(self, message: str):
        self.log_from_client(message)
        self.sock.send(message.encode("utf-8"))

    def receive(self):
        response = b''
        while True:
            try:
                string = self.sock.recv(1024)
                if string == b'':
                    break
                response += string
            except Exception:
                break

        message = response.decode('utf-8')
        self.log_from_server(message)
        answer = smtp_answer.from_str(message)
        if answer.has_error():
            raise SmtpServerException(answer.answer)

    def connect(self):
        self.print('Запуск SMTP клиента')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)

        try:
            print(f'Подключение к SMTP серверу [{self.server}:{self.port}]...')
            self.sock.connect((self.server, self.port))
            self.print_success('Подключение к серверу выполнено успешно')

            if self.use_ssl:
                print('Попытка установления защищённого соединения...')
                self.sock = self.start_ssl()
                self.print_success('Защищенное соединение успешно установлено')

        except SmtpServerException as e:
            self.sock.close()
            self.sock = None
            if not self.print_log:
                print(f'{RED}Произошла ошибка: \n{e.msg}{DEFAULT}')

        return self

    def close(self):
        if self.sock is not None:
            self.send("QUIT")
            self.sock.close()
        self.print_success('Соединение успешно закрыто')

    def send_mail(self, mail: str):
        if self.sock is None:
            print(f'{RED}Произошла ошибка: подключение к серверу не было установлено{DEFAULT}')

        print('Отправка сообщения...')
        try:
            for command in self.create_init_commands():
                self.send(command)
                if 'DATA' in command:
                    self.sock.send(mail.encode("utf-8"))
                self.receive()

        except SmtpServerException as e:
            print(f'{RED}Произошла ошибка: \n{e.msg}{DEFAULT}')
        except Exception:
            print(f'{RED}Произошла ошибка подключения{DEFAULT}')
        return self
