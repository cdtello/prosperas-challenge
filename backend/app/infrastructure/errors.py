import logging
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning(
            "HTTP %d — %s | path=%s request_id=%s",
            exc.status_code,
            exc.detail,
            request.url.path,
            _request_id(request),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": _request_id(request)},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "Validation error | path=%s request_id=%s errors=%s",
            request.url.path,
            _request_id(request),
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "request_id": _request_id(request)},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "request_id": _request_id(request)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        logger.error(
            "Unhandled %s | path=%s request_id=%s\n%s",
            type(exc).__name__,
            request.url.path,
            request_id,
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "request_id": request_id},
        )
