from fastapi import FastAPI

from api.routes import router
from infrastructure.config import load_smtp_config
from infrastructure.dotenv import load_dotenv
from infrastructure.smtp_email_sender import SmtpEmailSender


def create_app() -> FastAPI:
    load_dotenv()
    app = FastAPI(
        title="mail-sender",
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.email_sender_factory = _create_email_sender
    app.include_router(router)
    return app


def _create_email_sender() -> SmtpEmailSender:
    return SmtpEmailSender(load_smtp_config())
