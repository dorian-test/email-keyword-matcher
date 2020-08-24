import email
import imaplib
import smtplib
import ssl
import re
import typing


class EmailKeywordMatcher:

    def __init__(self, email_address: str = None, password: str = None, host: str = None, port: int = None):

        if email_address is None:
            email_address = input("Email: ")
        if password is None:
            password = input("Password: ")
        if host is None:
            host = input("Host: ")
        if port is None:
            port = input("Port: ")

        self._email = email_address

        self._smtp = smtplib.SMTP(host, port)
        self._smtp.starttls(context=ssl.create_default_context())
        self._smtp.login(email_address, password)

        self._imap = imaplib.IMAP4_SSL(host)
        self._imap.login(email_address, password)
        self._imap.select('Inbox')

        self._keyword_fns = {}

    def add_keyword(self, keyword: str, callback: typing.Callable):
        self._keyword_fns[keyword] = callback

    @property
    def keywords(self) -> typing.KeysView:
        return self._keyword_fns.keys()

    def send(self, to_email: str, subject: str, contents: str) -> None:
        message = f"Subject: {subject}\n\n{contents}\n\nKeywords: {self.keywords}"
        self._smtp.sendmail(self._email, to_email, message)

    def process_recieved(self, from_email: str, subject: str) -> None:
        keyword = self._get_keyword_response(from_email, subject)
        self._keyword_fns[keyword]()

    def _get_keyword_response(self, from_email: str, subject: str) -> str:
        payload = self._get_payload(from_email, subject)
        pattern = "|".join(self.keywords)
        match = re.match(pattern, payload, flags=re.I)
        return match.group()

    def _get_payload(self, from_email: str, subject: str) -> str:

        return_code, matches = self._imap.search(None, f'FROM "{from_email}" SUBJECT "{subject}"')
        if return_code != 'OK':
            raise RuntimeError(f"Got return code '{return_code}' from searching")

        return_code, data = self._imap.fetch(matches[0], '(RFC822)')
        if return_code != 'OK':
            raise RuntimeError(f"Got return code '{return_code}' from fetching")

        message = email.message_from_bytes(data[0][1])
        if message.is_multipart():
            return message.get_payload(0).get_payload()
        else:
            return message.get_payload(0)
