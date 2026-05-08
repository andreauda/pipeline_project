import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]) -> None:
    # base_dir - directory principale del progetto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # log_dir - directory per i log, con rotazione dei file
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, "pipeline.log") # percorso completo del file di log
    # log_level e log_format - configurazione del livello di log e del formato
    log_level = getattr(logging, config["logging"]["level"].upper())
    log_format = config["logging"]["format"]

    formatter = logging.Formatter(log_format)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5_000_000,
        backupCount=3
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)