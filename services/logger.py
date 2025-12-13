import logging
from datetime import datetime
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("ARTBAZAR")


def log_event(event: str, details: str = ""):
    logger.info(f"{event} | {details}")


def log_error(event: str, error: str):
    logger.error(f"{event} | ERROR: {error}")
