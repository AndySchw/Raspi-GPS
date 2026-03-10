#!/usr/bin/env python3
"""
Hauptprogramm für DIY Outdoor GPS Gerät

Startet alle Module und koordiniert die Geräte-Funktionen.
"""

import time
import signal
import sys
from pathlib import Path

# Füge src/ zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger
from src.utils.config import config

# Logger einrichten
logger = setup_logger("main", log_file="logs/gps_device.log")


class GPSDevice:
    """Haupt-Klasse für GPS-Gerät"""

    def __init__(self):
        """Initialisiert GPS-Gerät"""
        self.running = False

        # Module werden hier initialisiert (später)
        self.gps = None
        self.imu = None
        self.display = None
        self.navigator = None

        logger.info("GPS-Gerät initialisiert")

    def initialize_hardware(self) -> bool:
        """
        Initialisiert alle Hardware-Module

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        logger.info("Initialisiere Hardware-Module...")

        try:
            # TODO: GPS-Modul initialisieren
            # self.gps = NEOM8N(enable_mock=config.get('hardware.enable_mock'))
            # if not self.gps.initialize():
            #     logger.error("GPS-Initialisierung fehlgeschlagen")
            #     return False

            # TODO: IMU initialisieren
            # self.imu = MPU9250(enable_mock=config.get('hardware.enable_mock'))
            # if not self.imu.initialize():
            #     logger.error("IMU-Initialisierung fehlgeschlagen")
            #     return False

            # TODO: Display initialisieren
            # self.display = EPaperDisplay(enable_mock=config.get('hardware.enable_mock'))
            # if not self.display.initialize():
            #     logger.error("Display-Initialisierung fehlgeschlagen")
            #     return False

            logger.info("Alle Hardware-Module erfolgreich initialisiert")
            return True

        except Exception as e:
            logger.error(f"Fehler bei Hardware-Initialisierung: {e}")
            return False

    def main_loop(self):
        """Haupt-Event-Loop"""
        logger.info("Starte Haupt-Loop...")
        self.running = True

        update_counter = 0

        while self.running:
            try:
                # TODO: GPS-Daten lesen
                # gps_data = self.gps.read()

                # TODO: IMU-Daten lesen
                # imu_data = self.imu.read()

                # TODO: Navigation berechnen
                # nav_info = self.navigator.update(gps_data, imu_data)

                # TODO: Display aktualisieren
                # self.display.update(nav_info)

                # Placeholder: Ausgabe für Demo
                logger.debug(f"Update #{update_counter}")
                update_counter += 1

                # Warte bis zum nächsten Update
                update_interval = config.get('display.update_interval', 2.0)
                time.sleep(update_interval)

            except KeyboardInterrupt:
                logger.info("Programm durch Benutzer beendet")
                break
            except Exception as e:
                logger.error(f"Fehler im Haupt-Loop: {e}")
                time.sleep(1)  # Kurze Pause bei Fehlern

        self.cleanup()

    def cleanup(self):
        """Cleanup aller Ressourcen"""
        logger.info("Räume auf...")
        self.running = False

        # TODO: Hardware-Cleanup
        # if self.gps:
        #     self.gps.cleanup()
        # if self.imu:
        #     self.imu.cleanup()
        # if self.display:
        #     self.display.cleanup()

        logger.info("Cleanup abgeschlossen")

    def signal_handler(self, sig, frame):
        """Handler für SIGINT/SIGTERM"""
        logger.info(f"Signal {sig} empfangen, beende Programm...")
        self.running = False


def main():
    """Main Entry Point"""
    logger.info("=== GPS-Gerät gestartet ===")
    logger.info(f"Mock-Modus: {config.get('hardware.enable_mock', False)}")

    # GPS-Gerät erstellen
    device = GPSDevice()

    # Signal-Handler registrieren
    signal.signal(signal.SIGINT, device.signal_handler)
    signal.signal(signal.SIGTERM, device.signal_handler)

    # Hardware initialisieren
    if not device.initialize_hardware():
        logger.error("Hardware-Initialisierung fehlgeschlagen, beende Programm")
        sys.exit(1)

    # Haupt-Loop starten
    device.main_loop()

    logger.info("=== GPS-Gerät beendet ===")


if __name__ == "__main__":
    main()
