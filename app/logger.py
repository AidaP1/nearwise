import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO if os.getenv("FLASK_ENV") == "production" else logging.DEBUG)

    # Avoid adding multiple handlers if already configured
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Stream handler (Render captures stdout)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Optional: File handler (useful for local dev)
        if not os.getenv("RENDER"):  # Avoid using files on Render
            file_handler = RotatingFileHandler("app.log", maxBytes=1000000, backupCount=3)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
