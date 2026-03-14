#!/usr/bin/env python3
"""
GDEW029Z10 Display-Treiber
MH-ET LIVE 2.9" ePaper Display (Rot/Schwarz/Weiß)

Technische Details:
- Auflösung: 296x128 Pixel (Querformat)
- Controller: IL0373 / UC8151
- Farben: Schwarz, Weiß, Rot
- Interface: SPI

Wichtige Erkenntnisse:
- Schwarz-Buffer (0x24): 0x00=schwarz, 0xFF=weiß
- Rot-Buffer (0x26): 0x00=rot, 0xFF=transparent
- Update-Befehl: 0x20
- BUSY-Pin muss angeschlossen sein!
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont


class GDEW029Z10:
    """Display-Treiber für MH-ET LIVE 2.9" ePaper Display"""

    # Display-Spezifikationen
    WIDTH = 296
    HEIGHT = 128

    # SPI-Befehle
    CMD_BLACK_BUFFER = 0x24
    CMD_RED_BUFFER = 0x26
    CMD_UPDATE = 0x20

    def __init__(self, rst_pin=24, dc_pin=25, cs_pin=8, busy_pin=17, spi_speed=2000000):
        """
        Initialisiere Display-Treiber

        Args:
            rst_pin: Reset-Pin (GPIO BCM)
            dc_pin: Data/Command-Pin (GPIO BCM)
            cs_pin: Chip Select-Pin (GPIO BCM)
            busy_pin: Busy-Pin (GPIO BCM)
            spi_speed: SPI-Geschwindigkeit in Hz
        """
        self.rst_pin = rst_pin
        self.dc_pin = dc_pin
        self.cs_pin = cs_pin
        self.busy_pin = busy_pin

        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.busy_pin, GPIO.IN)

        # SPI Setup
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = spi_speed
        self.spi.mode = 0

    def _send_command(self, command):
        """Sende Befehl an Display"""
        GPIO.output(self.dc_pin, 0)  # DC=LOW für Command
        GPIO.output(self.cs_pin, 0)
        self.spi.xfer2([command])
        GPIO.output(self.cs_pin, 1)

    def _send_data(self, data):
        """Sende Daten an Display"""
        GPIO.output(self.dc_pin, 1)  # DC=HIGH für Data
        GPIO.output(self.cs_pin, 0)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(self.cs_pin, 1)

    def _wait_busy(self, timeout_sec=20):
        """
        Warte bis Display fertig ist (BUSY-Pin HIGH)

        Args:
            timeout_sec: Timeout in Sekunden

        Returns:
            bool: True wenn erfolgreich, False bei Timeout
        """
        start = time.time()
        while GPIO.input(self.busy_pin) == 0:
            if time.time() - start > timeout_sec:
                return False
            time.sleep(0.01)
        return True

    def reset(self):
        """Hardware-Reset des Displays"""
        GPIO.output(self.rst_pin, 0)
        time.sleep(0.2)
        GPIO.output(self.rst_pin, 1)
        time.sleep(0.5)

    def clear(self):
        """
        Lösche Display (komplett weiß)

        Returns:
            bool: True wenn erfolgreich
        """
        self.reset()

        bytes_total = int(self.WIDTH * self.HEIGHT / 8)

        # Schwarz-Buffer: alles weiß
        self._send_command(self.CMD_BLACK_BUFFER)
        for _ in range(bytes_total):
            self._send_data(0xFF)

        # Rot-Buffer: kein Rot
        self._send_command(self.CMD_RED_BUFFER)
        for _ in range(bytes_total):
            self._send_data(0xFF)

        # Update
        self._send_command(self.CMD_UPDATE)
        return self._wait_busy()

    def display(self, black_image, red_image):
        """
        Zeige Bild auf Display an

        Args:
            black_image: PIL Image (1-bit) für Schwarz/Weiß
            red_image: PIL Image (1-bit) für Rot

        Returns:
            bool: True wenn erfolgreich

        Beispiel:
            black_img = Image.new('1', (296, 128), 255)  # Weiß
            red_img = Image.new('1', (296, 128), 255)    # Weiß
            draw_black = ImageDraw.Draw(black_img)
            draw_red = ImageDraw.Draw(red_img)
            draw_black.text((10, 10), "Text", fill=0)  # Schwarz
            draw_red.rectangle((10, 30, 50, 50), fill=0)  # Rot
            epd.display(black_img, red_img)
        """
        # Validierung
        if black_image.size != (self.WIDTH, self.HEIGHT):
            raise ValueError(f"Schwarz-Bild muss {self.WIDTH}x{self.HEIGHT} sein")
        if red_image.size != (self.WIDTH, self.HEIGHT):
            raise ValueError(f"Rot-Bild muss {self.WIDTH}x{self.HEIGHT} sein")
        if black_image.mode != '1':
            black_image = black_image.convert('1')
        if red_image.mode != '1':
            red_image = red_image.convert('1')

        self.reset()

        # Schwarz-Buffer senden
        self._send_command(self.CMD_BLACK_BUFFER)
        black_bytes = black_image.tobytes()
        for byte in black_bytes:
            self._send_data(byte)

        # Rot-Buffer senden
        self._send_command(self.CMD_RED_BUFFER)
        red_bytes = red_image.tobytes()
        for byte in red_bytes:
            self._send_data(byte)

        # Display aktualisieren
        self._send_command(self.CMD_UPDATE)
        return self._wait_busy()

    def sleep(self):
        """Setze Display in Sleep-Modus (Energiesparen)"""
        # Kein spezieller Sleep-Befehl nötig
        # ePaper-Displays behalten Bild ohne Strom
        pass

    def cleanup(self):
        """Cleanup GPIO"""
        GPIO.cleanup()


# Beispiel-Nutzung
if __name__ == "__main__":
    print("GDEW029Z10 Display-Test")
    print("="*60)

    try:
        # Display initialisieren
        epd = GDEW029Z10()

        # Display löschen
        print("Lösche Display...")
        epd.clear()
        time.sleep(2)

        # Testbild erstellen
        print("Erstelle Testbild...")
        black_img = Image.new('1', (epd.WIDTH, epd.HEIGHT), 255)
        red_img = Image.new('1', (epd.WIDTH, epd.HEIGHT), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, epd.WIDTH-1, epd.HEIGHT-1), outline=0, width=3)

        # Schwarzer Text
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except:
            font = ImageFont.load_default()

        draw_black.text((10, 10), "GPS TRACKER", font=font, fill=0)

        # Rote Linie
        draw_red.line((10, 45, epd.WIDTH-10, 45), fill=0, width=2)

        # Schwarze Daten
        draw_black.text((10, 60), "Lat: 48.1234", fill=0)
        draw_black.text((10, 85), "Lon: 11.5678", fill=0)

        # Rote Status-Box
        draw_red.rectangle((200, 60, 280, 110), outline=0, width=2)

        # Anzeigen
        print("Zeige Bild...")
        epd.display(black_img, red_img)

        print("\n✅ Erfolgreich!")
        print("="*60)

    except KeyboardInterrupt:
        print("\nAbgebrochen")

    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

    finally:
        epd.cleanup()
