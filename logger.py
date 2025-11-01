# logger.py
import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
import os

LOG_FILENAME = "debate_log.txt"

def setup_logger(name: str = "debate_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(LOG_FILENAME) or ".", exist_ok=True)

    fh = RotatingFileHandler(LOG_FILENAME, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    ch = RichHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger
