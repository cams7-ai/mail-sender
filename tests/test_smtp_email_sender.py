from domain import EmailMessageData
from infrastructure import SmtpConfig
from infrastructure import SmtpEmailSender

def test_smtp_email_sender_uses_tls_and_login(monkeypatch):
    smtp_instances = []
    monkeypatch.setattr(
        "infrastructure.smtp_email_sender.smtplib.SMTP",
        lambda host, port: _make_smtp(host, port, smtp_instances),
    )
    config = SmtpConfig(
        host="smtp.example.com",
        port=587,
        sender="from@example.com",
        user="user",
        password="password",
        use_tls=True,
    )

    SmtpEmailSender(config).send(EmailMessageData("to@example.com", "Assunto", "Mensagem"))

    smtp = smtp_instances[0]
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 587
    assert smtp.started_tls is True
    assert smtp.login_args == ("user", "password")
    assert smtp.sent_message["From"] == "from@example.com"
    assert smtp.sent_message["To"] == "to@example.com"
    assert smtp.sent_message["Subject"] == "Assunto"
    assert smtp.sent_message.get_content().strip() == "Mensagem"
    assert smtp.closed is True


def test_smtp_email_sender_skips_tls_and_login_without_credentials(monkeypatch):
    smtp_instances = []
    monkeypatch.setattr(
        "infrastructure.smtp_email_sender.smtplib.SMTP",
        lambda host, port: _make_smtp(host, port, smtp_instances),
    )
    config = SmtpConfig(
        host="smtp.example.com",
        port=25,
        sender="from@example.com",
        use_tls=False,
    )

    SmtpEmailSender(config).send(EmailMessageData("to@example.com", "Assunto", "Mensagem"))

    smtp = smtp_instances[0]
    assert smtp.started_tls is False
    assert smtp.login_args is None


def test_smtp_email_sender_builds_html_message(monkeypatch):
    smtp_instances = []
    monkeypatch.setattr(
        "infrastructure.smtp_email_sender.smtplib.SMTP",
        lambda host, port: _make_smtp(host, port, smtp_instances),
    )
    config = SmtpConfig(
        host="smtp.example.com",
        port=25,
        sender="from@example.com",
        use_tls=False,
    )

    SmtpEmailSender(config).send(EmailMessageData("to@example.com", "Assunto", "<strong>Mensagem</strong>", "HTML"))

    smtp = smtp_instances[0]
    assert smtp.sent_message.is_multipart()
    html_part = smtp.sent_message.get_payload()[0]
    assert html_part.get_content_type() == "text/html"
    assert html_part.get_content().strip() == "<strong>Mensagem</strong>"


def _make_smtp(host, port, instances):
    smtp = FakeSMTP(host, port)
    instances.append(smtp)
    return smtp


class FakeSMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.login_args = None
        self.sent_message = None
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.closed = True

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.login_args = (user, password)

    def send_message(self, message):
        self.sent_message = message
