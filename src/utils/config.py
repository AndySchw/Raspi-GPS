"""
Konfigurations-Management für GPS-Gerät

Lädt Einstellungen aus YAML-Dateien und .env
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()


class Config:
    """Zentrale Konfigurations-Klasse"""

    def __init__(self, config_file: str = "config/default.yaml"):
        """
        Initialisiert Konfiguration

        Args:
            config_file: Pfad zur YAML-Konfigurationsdatei
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
        self._load_hardware_pins()

    def _load_hardware_pins(self):
        """Lädt Hardware-Pin-Konfiguration und merged sie in config"""
        pins_file = Path("config/hardware_pins.yaml")
        if pins_file.exists():
            with open(pins_file, 'r', encoding='utf-8') as f:
                pins_config = yaml.safe_load(f) or {}
                # Merge pins in hardware section
                if 'hardware' not in self.config:
                    self.config['hardware'] = {}
                self.config['hardware']['pins'] = pins_config

    def load(self):
        """Lädt Konfiguration aus YAML-Datei"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Default-Konfiguration wenn Datei nicht existiert
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Standard-Konfiguration"""
        return {
            'gps': {
                'baudrate': 9600,
                'port': '/dev/ttyS0',
                'update_rate': 1.0,  # Hz
            },
            'display': {
                'update_interval': 2.0,  # Sekunden
                'full_refresh_every': 10,  # Anzahl Updates
            },
            'navigation': {
                'step_length': 0.7,  # Meter
                'step_threshold': 1.2,  # g
                'step_cooldown': 0.3,  # Sekunden
            },
            'tracking': {
                'log_interval': 5.0,  # Sekunden
                'log_directory': 'data/tracks',
            },
            'web': {
                'host': '0.0.0.0',
                'port': 8080,
                'enable': True,
            },
            'hardware': {
                'enable_mock': False,  # Mock-Modus für Tests
                'i2c_bus': 1,
                'mpu9250_address': 0x68,
                'bmp180_address': 0x77,
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt Konfigurations-Wert (mit Punkt-Notation)

        Args:
            key: Konfigurations-Key (z.B. 'gps.baudrate')
            default: Default-Wert falls Key nicht existiert

        Returns:
            Konfigurations-Wert oder Default

        Beispiel:
            >>> config.get('gps.baudrate')
            9600
            >>> config.get('gps.invalid', 'fallback')
            'fallback'
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Setzt Konfigurations-Wert (mit Punkt-Notation)

        Args:
            key: Konfigurations-Key (z.B. 'gps.baudrate')
            value: Neuer Wert
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """Speichert Konfiguration in YAML-Datei"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)


# Globale Config-Instanz
config = Config()
