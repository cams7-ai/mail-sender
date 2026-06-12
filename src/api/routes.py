from smtplib import SMTPException
from typing import Callable

from fastapi import APIRouter, HTTPException, Request, status

from api.schemas import EmailRequest, EmailResponse
from application import SendEmailUseCase
from domain import EmailMessageData
from domain import ConfigurationError
from domain import EmailSender

router = APIRouter(prefix="/api/v1/mail", tags=["mail"])

@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_200_OK)
def send_email(payload: EmailRequest, request: Request):
    try:
        sender = _get_email_sender(request)
        use_case = SendEmailUseCase(sender)
        use_case.execute(
            EmailMessageData(
                recipient=str(payload.to),
                subject=payload.subject,
                body=payload.body,
            )
        )
    except ConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except SMTPException as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao enviar e-mail.") from exc

    return EmailResponse(message="E-mail enviado com sucesso.")


def _get_email_sender(request: Request) -> EmailSender:
    factory: Callable[[], EmailSender] | None = getattr(request.app.state, "email_sender_factory", None)
    if factory is None:
        raise ConfigurationError("Configuração de envio de e-mail ausente.")
    return factory()
