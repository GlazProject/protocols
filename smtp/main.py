import os
from argparse import ArgumentParser

from smtp_client import SmtpClient
from message_creator import MimeMailCreator


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-f', '--from', type=str, default='<>', dest='sender', help='Email адрес отправителя')
    parser.add_argument('-t', '--to', type=str, help='Email адрес получателя', required=True)
    parser.add_argument('--subject', type=str, default='Happy pictures',
                        help='Тема письма. По умолчанию “Hello there”')
    parser.add_argument('-d', '--directory', type=str, default='.', help='Папка с картинками для отправки. '
                                                                         'По умолчанию текущая директория')
    parser.add_argument('-s', '--server', type=str,
                        help='Адрес или домен SMTP сервера для использования в формате адрес[:порт]. '
                             'По умолчанию порт 25',
                        required=True)
    parser.add_argument('--ssl', action='store_true',
                        help='Использовать SSL при обращении к SMTP серверу')
    parser.add_argument('--auth', action='store_true', help='Необходима авторизация')
    parser.add_argument('-v', '--verbose', action='store_true', help='Выводить протокол работы')
    return parser.parse_args()


def create_message_with_images(sender: str, mail_to: str, subject: str, directory: str) -> str:
    creator = MimeMailCreator()\
        .with_header(sender, mail_to, subject)\
        .with_text(f"Это картинки из папки {directory}")

    for file in os.listdir(directory):
        if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp')):
            creator.with_image(directory + "/" + file)

    return creator.get_message()


if __name__ == '__main__':
    args = get_args()

    server, port = args.server.split(":")
    port = 25 if port is None else int(port)

    try:
        message = create_message_with_images(args.sender, args.to, args.subject, args.directory)
        SmtpClient(args.sender, args.to, server, port, args.ssl, args.auth, args.verbose)\
            .connect()\
            .send_mail(message)\
            .close()
    except Exception as e:
        print(e)
