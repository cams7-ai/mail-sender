from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.schemas import ErrorResponse
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
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.include_router(router)
    app.openapi = lambda: _custom_openapi(app)
    return app


def _create_email_sender():
    return SmtpEmailSender(load_smtp_config())


async def _http_exception_handler(_request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = detail.get("code", "http_error")
    message = detail.get("message", str(exc.detail))
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "not_found"
        message = "Recurso não encontrado."

    return _error_response(exc.status_code, code, message)


async def _validation_exception_handler(_request: Request, _exc: RequestValidationError):
    return _error_response(
        422,
        "validation_error",
        "Dados de entrada inválidos.",
    )


def _error_response(status_code: int, code: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error={"code": code, "message": message}).model_dump(),
    )


def _custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    schemas = openapi_schema.setdefault("components", {}).setdefault("schemas", {})
    schemas.pop("HTTPValidationError", None)
    schemas.pop("ValidationError", None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema
