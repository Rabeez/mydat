import logging
from collections.abc import Awaitable
from typing import Callable, ClassVar, final, override

from colorama import Fore, Style
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Define a custom formatter for colored output
@final
class ColorFormatter(logging.Formatter):
    COLORS: ClassVar = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.CYAN,
        "CRITICAL": Fore.MAGENTA,
    }

    @override
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


# Create a shared logger instance for the app
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Create a handler with custom formatting
handler = logging.StreamHandler()
formatter = ColorFormatter("%(levelname)s: %(message)s")
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
            raise HTTPException(400, "Missing client data")
        client_host, client_port = request.client.host, request.client.port
        logger.debug(f"Got a request from {client_host}:{client_port}")
        response = await call_next(request)
        return response
