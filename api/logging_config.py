import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.getenv("LOG_FILE", "app.log")

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)