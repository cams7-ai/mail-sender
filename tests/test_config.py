import os

import pytest

from domain import ConfigurationError
from infrastructure import SmtpConfig, load_smtp_config, parse_bool
from infrastructure import load_dotenv

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
def test_parse_bool_accepts_common_values(value, expected):
    assert parse_bool(value) is expected


def test_parse_bool_rejects_invalid_value():
    with pytest.raises(ConfigurationError, match="Valor booleano inválido"):
        parse_bool("talvez")


def test_load_dotenv_reads_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "SMTP_HOST=smtp.gmail.com",
                "SMTP_PORT=587",
                "# comentário ignorado",
                "",
                'SMTP_FROM="from@gmail.com"',
                "INVALID_LINE",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_PORT", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)

    load_dotenv(env_file)

    assert os.environ["SMTP_HOST"] == "smtp.gmail.com"
    assert os.environ["SMTP_PORT"] == "587"
    assert os.environ["SMTP_FROM"] == "from@gmail.com"


def test_load_dotenv_keeps_existing_environment_value(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("SMTP_HOST=smtp.gmail.com", encoding="utf-8")
    monkeypatch.setenv("SMTP_HOST", "existing.smtp.example.com")

    load_dotenv(env_file)

    assert os.environ["SMTP_HOST"] == "existing.smtp.example.com"


def test_load_dotenv_ignores_missing_file(tmp_path):
    load_dotenv(tmp_path / ".env")


def test_load_smtp_config_reads_environment(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "password")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "yes")

    config = load_smtp_config()

    assert config == SmtpConfig(
        host="smtp.example.com",
        port=587,
        user="user",
        password="password",
        sender="from@example.com",
        use_tls=True,
    )


def test_load_smtp_config_defaults_tls_to_true(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("SMTP_USE_TLS", raising=False)

    config = load_smtp_config()

    assert config.use_tls is True
    assert config.user is None
    assert config.password is None


def test_load_smtp_config_requires_host(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")

    with pytest.raises(ConfigurationError, match="servidor SMTP"):
        load_smtp_config()


def test_load_smtp_config_rejects_non_integer_port(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "invalid")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")

    with pytest.raises(ConfigurationError, match="número inteiro"):
        load_smtp_config()


def test_load_smtp_config_rejects_port_out_of_range(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "70000")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")

    with pytest.raises(ConfigurationError, match="1 e 65535"):
        load_smtp_config()
