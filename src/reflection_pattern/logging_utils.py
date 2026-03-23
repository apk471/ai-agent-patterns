from __future__ import annotations

import logging
import sys

RESET = "\033[0m"
COLORS = {
    logging.DEBUG: "\033[36m",  # Cyan
    logging.INFO: "\033[32m",  # Green
    logging.WARNING: "\033[33m",  # Yellow
    logging.ERROR: "\033[31m",  # Red
    logging.CRITICAL: "\033[35m",  # Magenta
}


class ColorFormatter(logging.Formatter):
    """Simple color formatter for terminal logs."""

    def __init__(self, use_color: bool = True) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        if not self.use_color:
            return rendered
        color = COLORS.get(record.levelno, "")
        if not color:
            return rendered
        return f"{color}{rendered}{RESET}"


def configure_logging(verbosity: int = 1) -> None:
    """Configure root logging with colored terminal output."""
    if verbosity <= 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    use_color = sys.stderr.isatty()
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter(use_color=use_color))

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
