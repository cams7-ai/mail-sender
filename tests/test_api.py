from smtplib import SMTPException

from fastapi.testclient import TestClient

import main
from api.server import create_app
from domain import ConfigurationError


def test_main_exposes_fastapi_app():
    assert main.app.title == "mail-sender"


def test_main_run_starts_uvicorn(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "load_dotenv", lambda: None)
    monkeypatch.delenv("API_HOST", raising=False)
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.setattr(main.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    main.run()

    assert calls == [(("main:app",), {"host": "0.0.0.0", "port": 8000, "reload": False})]


def test_create_app_configures_email_sender_factory():
    app = create_app()

    assert callable(app.state.email_sender_factory)
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


def test_create_app_default_factory_builds_smtp_sender(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("SMTP_USE_TLS", raising=False)
    app = create_app()

    sender = app.state.email_sender_factory()

    assert sender._config.host == "smtp.example.com"


def test_send_email_endpoint_returns_success():
    client, sender = _make_client(FakeEmailSender())

    response = client.post(
        "/api/v1/mail/send",
        json={
            "to": "to@example.com",
            "subject": "Assunto",
            "body": "Mensagem",
            "message_type": "HTML",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "E-mail enviado com sucesso."}
    assert sender.messages[0].recipient == "to@example.com"
    assert sender.messages[0].subject == "Assunto"
    assert sender.messages[0].body == "Mensagem"
    assert sender.messages[0].message_type == "HTML"


def test_documentation_endpoints_are_available():
    client, _sender = _make_client(FakeEmailSender())

    swagger_response = client.get("/docs")
    redoc_response = client.get("/redoc")
    openapi_response = client.get("/openapi.json")

    assert swagger_response.status_code == 200
    assert "Swagger UI" in swagger_response.text
    assert redoc_response.status_code == 200
    assert "ReDoc" in redoc_response.text
    assert openapi_response.status_code == 200
    assert openapi_response.json()["info"]["title"] == "mail-sender"
    schemas = openapi_response.json()["components"]["schemas"]
    assert "ErrorResponse" in schemas
    assert "HTTPValidationError" not in schemas
    assert "ValidationError" not in schemas
    assert openapi_response.json() == client.get("/openapi.json").json()


def test_send_email_endpoint_rejects_invalid_payload():
    client, _sender = _make_client(FakeEmailSender())

    response = client.post(
        "/api/v1/mail/send",
        json={"to": "invalid", "subject": "", "body": ""},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "validation_error",
            "message": "Dados de entrada inválidos.",
        }
    }


def test_send_email_endpoint_returns_503_for_configuration_error():
    client, _sender = _make_client(FakeEmailSender(error=ConfigurationError("Configuração inválida.")))

    response = client.post(
        "/api/v1/mail/send",
        json={
            "to": "to@example.com",
            "subject": "Assunto",
            "body": "Mensagem",
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "configuration_error",
            "message": "Configuração inválida.",
        }
    }


def test_send_email_endpoint_returns_500_for_smtp_error():
    client, _sender = _make_client(FakeEmailSender(error=SMTPException("connection failed")))

    response = client.post(
        "/api/v1/mail/send",
        json={
            "to": "to@example.com",
            "subject": "Assunto",
            "body": "Mensagem",
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "email_send_error",
            "message": "Falha ao enviar e-mail.",
        }
    }


def test_send_email_endpoint_returns_503_without_factory():
    app = create_app()
    del app.state.email_sender_factory
    client = TestClient(app)

    response = client.post(
        "/api/v1/mail/send",
        json={
            "to": "to@example.com",
            "subject": "Assunto",
            "body": "Mensagem",
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "configuration_error",
            "message": "Configuração de envio de e-mail ausente.",
        }
    }


def test_unknown_endpoint_returns_error_response():
    client, _sender = _make_client(FakeEmailSender())

    response = client.get("/api/v1/mail/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Recurso não encontrado.",
        }
    }


def _make_client(sender):
    app = create_app()
    app.state.email_sender_factory = lambda: sender
    return TestClient(app), sender


class FakeEmailSender:
    def __init__(self, error=None):
        self.error = error
        self.messages = []

    def send(self, message):
        if self.error:
            raise self.error
        self.messages.append(message)
