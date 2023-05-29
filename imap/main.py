from argparse import ArgumentParser

from imap_client import ImapClient
from utils import RED, DEFAULT


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-u', '--user', type=str, dest='login', help='Email адрес почтового ящика', required=True)
    parser.add_argument('-s', '--server', type=str,
                        help='Адрес или домен IMAP сервера для подключения в формате адрес[:порт]. '
                             'По умолчанию порт 143',
                        required=True)
    parser.add_argument('-n', dest='messages', type=int, nargs='+',
                        default=[1],
                        help='Количество писем в формате N1 [N2]. По умолчанию 1')
    parser.add_argument('--ssl', action='store_true',
                        help='Использовать SSL при обращении к IMAP серверу')
    parser.add_argument('-d', '--mailbox', type=str, default='Inbox',
                        help='Имя папки с сообщениями (регистр важен')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    server = args.server.split(":")
    if len(server) == 1:
        port = 143
        server = server[0]
    else:
        port = int(server[1])
        server = server[0]

    if len(args.messages) == 1:
        m_from = m_to = args.messages[0]
    else:
        m_from = args.messages[0]
        m_to = args.messages[1]

    try:
        client = ImapClient(args.login, server, port, args.ssl)\
            .connect()\
            .read(m_from, m_to, args.mailbox)\
            .close()
    except Exception as e:
        print(f'{RED}Произошла ошибка: \n{e}{DEFAULT}')
