from __future__ import annotations

import argparse
import os
import smtplib
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}

@dataclass(frozen=True)
class MailConfig:
    host: str
    port: int
    sender: str
    recipient: str
    subject: str
    body: str
    user: str | None = None
    password: str | None = None
    use_tls: bool = True


class ConfigError(ValueError):
    """Indica configuração obrigatória ausente ou inválida."""


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name and name not in os.environ:
            os.environ[name] = value


def parse_bool(value: str | bool | None) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ConfigError(f"Valor booleano inválido: {value!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Envia um e-mail usando SMTP.")
    parser.add_argument("--to", dest="recipient", help="Endereço de e-mail do destinatário.")
    parser.add_argument("--subject", help="Assunto do e-mail.")
    parser.add_argument("--body", help="Corpo do e-mail em texto puro.")
    parser.add_argument("--from", dest="sender", help="Endereço de e-mail do remetente.")
    parser.add_argument("--host", help="Servidor SMTP.")
    parser.add_argument("--port", help="Porta do servidor SMTP.")
    parser.add_argument("--user", help="Usuário SMTP.")
    parser.add_argument("--password", help="Senha SMTP.")

    tls_group = parser.add_mutually_exclusive_group()
    tls_group.add_argument("--use-tls", dest="use_tls", action="store_true", default=None, help="Habilita STARTTLS.")
    tls_group.add_argument("--no-use-tls", dest="use_tls", action="store_false", help="Desabilita STARTTLS.")
    return parser

def _first_text_value(cli_value: str | None, env_name: str) -> str | None:
    return cli_value if cli_value is not None else os.getenv(env_name)


def _first_bool_value(cli_value: bool | None, env_name: str) -> str | bool | None:
    return cli_value if cli_value is not None else os.getenv(env_name)


def _required(value: str | None, field_name: str) -> str:
    if value is None or value == "":
        raise ConfigError(f"Configuração obrigatória ausente: {field_name}")
    return value

def _parse_port(value: str | None) -> int:
    raw_port = _required(value, "SMTP port")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ConfigError("A porta SMTP deve ser um número inteiro") from exc

    if port < 1 or port > 65535:
        raise ConfigError("A porta SMTP deve estar entre 1 e 65535")
    return port


def load_config(args: argparse.Namespace) -> MailConfig:
    host = _required(_first_text_value(args.host, "SMTP_HOST"), "servidor SMTP")
    port = _parse_port(_first_text_value(args.port, "SMTP_PORT"))
    sender = _required(_first_text_value(args.sender, "SMTP_FROM"), "remetente")
    recipient = _required(args.recipient, "destinatário")
    subject = _required(args.subject, "assunto")
    body = _required(args.body, "corpo")
    user = _first_text_value(args.user, "SMTP_USER")
    password = _first_text_value(args.password, "SMTP_PASSWORD")

    tls_value = _first_bool_value(args.use_tls, "SMTP_USE_TLS")
    use_tls = True if tls_value is None else parse_bool(tls_value)

    return MailConfig(
        host=host,
        port=port,
        sender=sender,
        recipient=recipient,
        subject=subject,
        body=body,
        user=user or None,
        password=password or None,
        use_tls=use_tls,
    )


def build_message(config: MailConfig) -> EmailMessage:
    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = config.recipient
    message["Subject"] = config.subject
    message.set_content(config.body)
    return message


def send_email(config: MailConfig) -> None:
    message = build_message(config)
    with smtplib.SMTP(config.host, config.port) as smtp:
        if config.use_tls:
            smtp.starttls()
        if config.user and config.password:
            smtp.login(config.user, config.password)
        smtp.send_message(message)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args)
        send_email(config)
    except ConfigError as exc:
        parser.error(str(exc))
    except smtplib.SMTPException as exc:
        print(f"Falha ao enviar e-mail: {exc}", file=sys.stderr)
        return 1

    print("E-mail enviado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
