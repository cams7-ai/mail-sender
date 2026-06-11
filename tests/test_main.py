from __future__ import annotations

import argparse
import smtplib

import pytest

import main


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        (True, True),
        (False, False),
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("off", False),
    ],
)
def test_parse_bool(value, expected):
    assert main.parse_bool(value) is expected


def test_parse_bool_rejects_invalid_value():
    with pytest.raises(main.ConfigError, match="Valor booleano"):
        main.parse_bool("maybe")


def test_load_dotenv_reads_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "SMTP_HOST=smtp.gmail.com",
                "SMTP_PORT=587",
                "# ignored comment",
                "",
                'SMTP_FROM="from@gmail.com"',
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_PORT", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)

    main.load_dotenv(env_file)

    assert main.os.environ["SMTP_HOST"] == "smtp.gmail.com"
    assert main.os.environ["SMTP_PORT"] == "587"
    assert main.os.environ["SMTP_FROM"] == "from@gmail.com"


def test_load_dotenv_keeps_existing_environment_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("SMTP_HOST=smtp.gmail.com", encoding="utf-8")
    monkeypatch.setenv("SMTP_HOST", "existing.smtp.example.com")

    main.load_dotenv(env_file)

    assert main.os.environ["SMTP_HOST"] == "existing.smtp.example.com"


def test_load_config_uses_cli_over_environment(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "env.smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "2525")
    monkeypatch.setenv("SMTP_USER", "env-user")
    monkeypatch.setenv("SMTP_PASSWORD", "env-password")
    monkeypatch.setenv("SMTP_FROM", "env@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")

    args = argparse.Namespace(
        host="cli.smtp.example.com",
        port="587",
        user="cli-user",
        password="cli-password",
        sender="cli@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=True,
    )

    config = main.load_config(args)

    assert config.host == "cli.smtp.example.com"
    assert config.port == 587
    assert config.user == "cli-user"
    assert config.password == "cli-password"
    assert config.sender == "cli@example.com"
    assert config.recipient == "to@example.com"
    assert config.subject == "Subject"
    assert config.body == "Body"
    assert config.use_tls is True


def test_load_config_reads_environment(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "password")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "yes")

    args = argparse.Namespace(
        host=None,
        port=None,
        user=None,
        password=None,
        sender=None,
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=None,
    )

    config = main.load_config(args)

    assert config == main.MailConfig(
        host="smtp.example.com",
        port=587,
        user="user",
        password="password",
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=True,
    )


def test_load_config_requires_mandatory_fields(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    args = argparse.Namespace(
        host=None,
        port="587",
        user=None,
        password=None,
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=None,
    )

    with pytest.raises(main.ConfigError, match="servidor SMTP"):
        main.load_config(args)


def test_load_config_validates_port():
    args = argparse.Namespace(
        host="smtp.example.com",
        port="invalid",
        user=None,
        password=None,
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=None,
    )

    with pytest.raises(main.ConfigError, match="número inteiro"):
        main.load_config(args)


def test_build_message_sets_headers_and_body():
    config = main.MailConfig(
        host="smtp.example.com",
        port=587,
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
    )

    message = main.build_message(config)

    assert message["From"] == "from@example.com"
    assert message["To"] == "to@example.com"
    assert message["Subject"] == "Subject"
    assert message.get_content().strip() == "Body"


def test_send_email_uses_tls_and_login(monkeypatch):
    smtp_instances = []
    monkeypatch.setattr(main.smtplib, "SMTP", lambda host, port: _make_smtp(host, port, smtp_instances))
    config = main.MailConfig(
        host="smtp.example.com",
        port=587,
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        user="user",
        password="password",
        use_tls=True,
    )

    main.send_email(config)

    smtp = smtp_instances[0]
    assert smtp.host == "smtp.example.com"
    assert smtp.port == 587
    assert smtp.started_tls is True
    assert smtp.login_args == ("user", "password")
    assert smtp.sent_message["To"] == "to@example.com"
    assert smtp.closed is True


def test_send_email_skips_login_without_credentials(monkeypatch):
    smtp_instances = []
    monkeypatch.setattr(main.smtplib, "SMTP", lambda host, port: _make_smtp(host, port, smtp_instances))
    config = main.MailConfig(
        host="smtp.example.com",
        port=25,
        sender="from@example.com",
        recipient="to@example.com",
        subject="Subject",
        body="Body",
        use_tls=False,
    )

    main.send_email(config)

    smtp = smtp_instances[0]
    assert smtp.started_tls is False
    assert smtp.login_args is None
    assert smtp.sent_message["Subject"] == "Subject"


def test_main_returns_one_on_smtp_error(monkeypatch, capsys):
    def fail_send_email(config):
        raise smtplib.SMTPException("connection failed")

    monkeypatch.setattr(main, "send_email", fail_send_email)

    code = main.main(
        [
            "--host",
            "smtp.example.com",
            "--port",
            "587",
            "--from",
            "from@example.com",
            "--to",
            "to@example.com",
            "--subject",
            "Subject",
            "--body",
            "Body",
        ]
    )

    assert code == 1
    assert "connection failed" in capsys.readouterr().err


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
