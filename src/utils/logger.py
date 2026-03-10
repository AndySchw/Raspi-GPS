"""
Logging-Konfiguration für GPS-Gerät
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "gps_device",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Konfiguriert Logger für das Projekt

    Args:
        name: Logger-Name
        level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional: Pfad zur Log-Datei

    Returns:
        Konfigurierter Logger

    Beispiel:
        >>> logger = setup_logger("gps", logging.DEBUG)
        >>> logger.info("GPS initialisiert")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Verhindere doppelte Handler
    if logger.handlers:
        return logger

    # Format für Log-Nachrichten
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Standard-Logger für das Projekt
logger = setup_logger("gps_device", logging.INFO, "logs/gps_device.log")
