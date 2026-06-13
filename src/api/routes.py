from smtplib import SMTPException
from typing import Callable

from fastapi import APIRouter, HTTPException, Request, status

from api.schemas import EmailRequest, EmailResponse, ErrorResponse
from application import SendEmailUseCase
from domain import EmailMessageData
from domain import ConfigurationError
from domain import EmailSender

router = APIRouter(prefix="/api/v1/mail", tags=["mail"])


ERROR_RESPONSES = {
    422: {"model": ErrorResponse, "description": "Dados de entrada inválidos."},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Erro interno ao enviar e-mail."},
    status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse, "description": "Configuração de e-mail indisponível."},
}


@router.post(
    "/send",
    response_model=EmailResponse,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
def send_email(payload: EmailRequest, request: Request):
    try:
        sender = _get_email_sender(request)
        use_case = SendEmailUseCase(sender)
        use_case.execute(
            EmailMessageData(
                recipient=str(payload.to),
                subject=payload.subject,
                body=payload.body,
                message_type=payload.message_type,
            )
        )
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "configuration_error", "message": str(exc)},
        ) from exc
    except SMTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "email_send_error", "message": "Falha ao enviar e-mail."},
        ) from exc

    return EmailResponse(message="E-mail enviado com sucesso.")


def _get_email_sender(request: Request) -> EmailSender:
    factory: Callable[[], EmailSender] | None = getattr(request.app.state, "email_sender_factory", None)
    if factory is None:
        raise ConfigurationError("Configuração de envio de e-mail ausente.")
    return factory()
