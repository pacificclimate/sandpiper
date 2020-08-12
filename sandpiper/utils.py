import logging

logger = logging.getLogger()

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: sandpiper: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
