"""Send emails and perform callbacks on keyword replies."""
import email
import imaplib
import smtplib
import ssl
import typing
import re


class EmailKeywordMatcher:
    """Send emails and perform callbacks on keyword replies."""

    def __init__(
            self,
            email_address: str = None,
            password: str = None,
            host: str = None,
            port: int = None,
    ):
        """
        Initialize the EmailKeywordMatcher.

        :param email_address: the email address that you will send from
        :param password: the password to that email address
        :param host: the host url (e.g., 'smtp.gmail.com')
        :param port: the port that the host uses
        """
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
        """Create a keyword that will be checked in the reply email."""
        self._keyword_fns[keyword] = callback

    @property
    def keywords(self) -> typing.KeysView:
        """Get current keywords."""
        return self._keyword_fns.keys()

    def send(self, to_email: str, subject: str, contents: str) -> None:
        """Send mail and include the available keywords in the message."""
        message = email.message.EmailMessage()
        message.set_content(f"{contents}\n\nKeywords: {list(self.keywords)}")
        message['to'] = to_email
        message['from'] = self._email
        message['subject'] = subject
        self._smtp.send_message(message)

    def is_response(self, from_email: str, subject: str) -> bool:
        """
        Return `True` if an email reply is in the inbox.

        Note: doesn't modify matches read status.
        """
        return len(self.get_response(from_email, subject)) > 0

    def get_response(
            self, from_email: str, subject: str) -> typing.List:
        """
        Return the message ids if there are any matches.

        Note: doesn't modify matches read status.
        """
        # this allows imap to refresh otherwise it sees no new mail
        self._imap.noop()
        return_code, matches = self._imap.search(
            None,
            f'FROM "{from_email}"',
            f'SUBJECT "{subject}"',
            '(UNSEEN)',
        )
        if return_code != 'OK':
            raise RuntimeError(
                f"Got return code '{return_code}' from searching")
        return matches if matches != [b''] else []

    def process_received(self, from_email: str, subject: str) -> None:
        """
        Perform the associated keyword's callback.

        Note: MODIFIES message fetched to be seen.
        """
        message = self._get_response(from_email, subject)
        keyword = self._get_keyword_response(message)
        if keyword:
            self._keyword_fns[keyword]()
        else:
            self.send(from_email,
                      f"Keyword not recognized for '{subject}'", '')

    def _get_response(
            self,
            from_email: str,
            subject: str,
    ) -> email.message.EmailMessage:
        """Return the response email message."""
        matches = self.get_response(from_email, subject)
        if not matches:
            raise RuntimeError('No messages found')

        return_code, data = self._imap.fetch(matches[0], '(RFC822)')
        if return_code != 'OK':
            raise RuntimeError(
                f"Got return code '{return_code}' from fetching")

        return email.message_from_bytes(data[0][1],
                                        _class=email.message.EmailMessage)

    def _get_keyword_response(
            self,
            message: email.message.EmailMessage
    ) -> str:
        """
        Return a match if there is one.

        Note: MODIFIES message fetched to be seen.
        """
        payload = self._get_payload(message)
        pattern = "|".join(self.keywords)
        match = re.match(pattern, payload, flags=re.I)
        if match:
            return match.group()
        else:
            return ''

    def _get_payload(self, message: email.message.EmailMessage) -> str:
        """
        Get the body of the email.

        Note: MODIFIES message fetched to be seen.
        """
        if message.is_multipart():
            return message.get_payload(0).get_payload()
        else:
            return message.get_payload(0)
