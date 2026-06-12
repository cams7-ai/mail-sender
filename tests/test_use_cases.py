from application import SendEmailUseCase
from domain import EmailMessageData
from domain import EmailSender


def test_send_email_use_case_calls_email_sender():
    sender = FakeEmailSender()
    message = EmailMessageData(
        recipient="to@example.com",
        subject="Assunto",
        body="Mensagem",
    )

    SendEmailUseCase(sender).execute(message)

    assert sender.messages == [message]


def test_email_sender_protocol_method_is_defined():
    EmailSender.send(FakeEmailSender(), EmailMessageData("to@example.com", "Assunto", "Mensagem"))


class FakeEmailSender:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)
