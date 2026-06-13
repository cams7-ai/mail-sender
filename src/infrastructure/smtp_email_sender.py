from email.message import EmailMessage
import smtplib

from domain import EmailMessageData
from infrastructure import SmtpConfig

class SmtpEmailSender:
    def __init__(self, config: SmtpConfig) -> None:
        self._config = config

    def send(self, message: EmailMessageData) -> None:
        email_message = self._build_message(message)
        with smtplib.SMTP(self._config.host, self._config.port) as smtp:
            if self._config.use_tls:
                smtp.starttls()
            if self._config.user and self._config.password:
                smtp.login(self._config.user, self._config.password)
            smtp.send_message(email_message)

    def _build_message(self, message: EmailMessageData) -> EmailMessage:
        email_message = EmailMessage()
        email_message["From"] = self._config.sender
        email_message["To"] = message.recipient
        email_message["Subject"] = message.subject
        if message.message_type == "HTML":
            email_message.add_alternative(message.body, subtype="html")
        else:
            email_message.set_content(message.body)
        return email_message
