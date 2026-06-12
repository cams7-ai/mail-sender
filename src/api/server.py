from fastapi import FastAPI

from api.routes import router
from infrastructure import load_smtp_config
from infrastructure import SmtpEmailSender

def create_app():
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

def _create_email_sender():
    return SmtpEmailSender(load_smtp_config())
