import logging
import os
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)

def create_logger(name: str, log_file: str, level=logging.INFO):
    """
    Creates (or reuses) a named logger with rotating file + console output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = RotatingFileHandler(
        f"logs/{log_file}", 
        mode="a",
        maxBytes=5_000_000,  # 5 MB
        backupCount=3        # keep up to 3 old log files
    )
    formatter = logging.Formatter(
        "%(name)s | %(module)s | %(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger