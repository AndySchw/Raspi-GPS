"""
Utility-Module für GPS-Gerät
"""

from .config import Config, config
from .logger import setup_logger, logger

__all__ = ['Config', 'config', 'setup_logger', 'logger']
