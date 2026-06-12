from smtplib import SMTPException

from fastapi.testclient import TestClient

import main
from api.app import create_app
from domain.exceptions import ConfigurationError


def test_main_exposes_fastapi_app():
    assert main.app.title == "mail-sender"


def test_main_run_starts_uvicorn(monkeypatch):
    calls = []
    monkeypatch.setattr(main.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    main.run()

    assert calls == [(("main:app",), {"host": "127.0.0.1", "port": 8000, "reload": True})]


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
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "E-mail enviado com sucesso."}
    assert sender.messages[0].recipient == "to@example.com"
    assert sender.messages[0].subject == "Assunto"
    assert sender.messages[0].body == "Mensagem"


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


def test_send_email_endpoint_rejects_invalid_payload():
    client, _sender = _make_client(FakeEmailSender())

    response = client.post(
        "/api/v1/mail/send",
        json={"to": "invalid", "subject": "", "body": ""},
    )

    assert response.status_code == 422


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
    assert response.json() == {"detail": "Configuração inválida."}


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
    assert response.json() == {"detail": "Falha ao enviar e-mail."}


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
    assert response.json() == {"detail": "Configuração de envio de e-mail ausente."}


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
