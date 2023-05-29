import base64
import datetime

from utils import get_base64_str


class MimeMailCreator:
    boundary = "my&unique&delimiter"

    def __init__(self):
        self._mail = ""

    def with_header(self, addr_from: str, addr_to: str, subject: str):
        self._mail += f'From: =?utf-8?B?{get_base64_str(addr_from)}?= <{addr_from}>\n' \
                      f'To: =?utf-8?B?{get_base64_str(addr_to)}?= <{addr_to}>\n' \
                      f'Date: {datetime.datetime.now().strftime("%a, %d %b %Y %H:%M%S GMT+5")}\n' \
                      f'Subject: {subject}\n' \
                      f'Content-Type: multipart/mixed; boundary={self.boundary}\n'
        return self

    def with_text(self, message: str):
        self._mail += f'\n\n--{self.boundary}' \
                      f'\nContent-Type: text/plain; charset="utf-8"' \
                      f'\nContent-Transfer-Encoding: quoted-printable' \
                      f'\n\n{message}'
        return self

    def with_image(self, image_path: str):
        with open(image_path, 'rb') as file:
            file_data = base64.b64encode(file.read()).decode('utf-8')
        image_type = image_path.split(".")[-1]
        image_name = get_base64_str(image_path.split("/")[-1])
        self._mail += f'\n\n--{self.boundary}' \
                      f'\nMime-Version: 1.0' \
                      f'\nContent-Type: image/{image_type}' \
                      f'\nContent-Transfer-Encoding: base64' \
                      f'\nContent-Disposition: attachment; filename="=?UTF-8?B?{image_name}?="\n\n'
        self._mail += file_data
        return self

    def get_message(self) -> str:
        self._mail += f'\n--{self.boundary}--\n.\r\n'
        return self._mail
