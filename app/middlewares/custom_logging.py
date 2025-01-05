import logging
from typing import ClassVar, final, override

from colorama import Fore, Style


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


# Configure logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = ColorFormatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.propagate = False
