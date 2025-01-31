import logging
from collections.abc import Awaitable
from pathlib import Path
from typing import Callable, ClassVar, final, override

from colorama import Fore, Style
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# Define a custom formatter for colored output
@final
class ColorFormatter(logging.Formatter):
    COLORS: ClassVar = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.BLUE,
        "CRITICAL": Fore.MAGENTA,
    }
    GRAY = Fore.LIGHTBLACK_EX
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    @override
    def format(self, record: logging.LogRecord) -> str:
        color_severity = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        record.levelname = f"{color_severity}{record.levelname}{reset}"

        timestamp = self.formatTime(record, self.datefmt)
        sep = "|"

        # Include filename and line number only for project files
        if Path(record.pathname).resolve().is_relative_to(self.PROJECT_ROOT):
            meta = f"{self.GRAY}{record.filename}:{record.lineno}{sep}{timestamp}{reset}"
            fmt = f"%(levelname)s{sep}{meta}{sep} %(message)s"
        else:
            meta = f"{self.GRAY}{timestamp}{reset}"
            fmt = f"%(levelname)s{sep}{meta}{sep} %(message)s"

        self._style._fmt = fmt  # Update formatter dynamically

        return super().format(record)


# Create a shared logger instance for the app
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Create a handler with custom formatting
handler = logging.StreamHandler()
formatter = ColorFormatter(datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

# Assign the handler to the shared logger
logger.handlers = [handler]
logger.propagate = False

# Configure uvicorn loggers to use the same formatter
for uvicorn_logger_name in ("uvicorn", "uvicorn.access"):
    uvicorn_logger = logging.getLogger(uvicorn_logger_name)
    uvicorn_logger.setLevel(logging.DEBUG)
    uvicorn_logger.handlers = [handler]
    uvicorn_logger.propagate = False


class LogClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not request.client:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing client data")
        client_host, client_port = request.client.host, request.client.port
        logger.debug(f"Got a request from {client_host}:{client_port}")
        response = await call_next(request)
        return response


class LogExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            response = await call_next(request)
        # TODO: Define application-specific empty exception here
        # custom exception -> 422
        # any other exception -> 500
        except Exception as e:
            logger.exception("An error occured during processing of request")
            response = ORJSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": type(e).__name__,
                    "msg": str(e),
                },
            )
        return response
