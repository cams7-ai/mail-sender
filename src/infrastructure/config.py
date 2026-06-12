from dataclasses import dataclass
import os

from domain.exceptions import ConfigurationError

TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    sender: str
    user: str | None = None
    password: str | None = None
    use_tls: bool = True


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
    raise ConfigurationError(f"Valor booleano inválido: {value!r}")


def load_smtp_config() -> SmtpConfig:
    tls_value = os.getenv("SMTP_USE_TLS")
    return SmtpConfig(
        host=_required(os.getenv("SMTP_HOST"), "servidor SMTP"),
        port=_parse_port(os.getenv("SMTP_PORT")),
        sender=_required(os.getenv("SMTP_FROM"), "remetente"),
        user=os.getenv("SMTP_USER") or None,
        password=os.getenv("SMTP_PASSWORD") or None,
        use_tls=True if tls_value is None else parse_bool(tls_value),
    )


def _required(value: str | None, field_name: str) -> str:
    if value is None or value == "":
        raise ConfigurationError(f"Configuração obrigatória ausente: {field_name}")
    return value


def _parse_port(value: str | None) -> int:
    raw_port = _required(value, "porta SMTP")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise ConfigurationError("A porta SMTP deve ser um número inteiro.") from exc

    if port < 1 or port > 65535:
        raise ConfigurationError("A porta SMTP deve estar entre 1 e 65535.")
    return port
