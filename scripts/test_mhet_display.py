#!/usr/bin/env python3
"""
Test-Script für MH-ET LIVE 2.9" ePaper Display
GDEW029Z10 - Rot/Schwarz/Weiß

Basierend auf dem Arduino-Code aus dem AZ-Delivery Datenblatt
"""

import sys
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Pin-Definitionen (wie im Datenblatt)
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# Display-Spezifikationen
EPD_WIDTH = 128
EPD_HEIGHT = 296

class GDEW029Z10:
    """Treiber für MH-ET LIVE 2.9inch ePaper (GDEW029Z10)"""

    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.spi = None

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    def spi_transfer(self, data):
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)

    def send_command(self, command):
        self.digital_write(DC_PIN, GPIO.LOW)
        self.digital_write(CS_PIN, GPIO.LOW)
        self.spi_transfer(command)
        self.digital_write(CS_PIN, GPIO.HIGH)

    def send_data(self, data):
        self.digital_write(DC_PIN, GPIO.HIGH)
        self.digital_write(CS_PIN, GPIO.LOW)
        self.spi_transfer(data)
        self.digital_write(CS_PIN, GPIO.HIGH)

    def wait_until_idle(self):
        """Warte bis BUSY-Pin HIGH ist (Display fertig)"""
        print("  Warte auf Display (BUSY-Pin)...", end='', flush=True)
        timeout = 0
        while self.digital_read(BUSY_PIN) == GPIO.LOW:
            self.delay_ms(100)
            timeout += 1
            if timeout > 100:  # 10 Sekunden Timeout
                print(" TIMEOUT!")
                return
            if timeout % 10 == 0:
                print(".", end='', flush=True)
        print(" OK")

    def reset(self):
        """Hardware-Reset"""
        print("  Hardware-Reset...")
        self.digital_write(RST_PIN, GPIO.HIGH)
        self.delay_ms(200)
        self.digital_write(RST_PIN, GPIO.LOW)
        self.delay_ms(10)
        self.digital_write(RST_PIN, GPIO.HIGH)
        self.delay_ms(200)

    def init(self):
        """Initialisiere Display"""
        print("\n1. Initialisiere GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        print("2. Initialisiere SPI...")
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000

        print("3. Reset Display...")
        self.reset()

        print("4. Sende Init-Befehle...")
        self.wait_until_idle()

        self.send_command(0x12)  # SWRESET
        self.wait_until_idle()

        self.send_command(0x01)  # Driver output control
        self.send_data(0x27)
        self.send_data(0x01)
        self.send_data(0x00)

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.send_command(0x44)  # Set RAM X address
        self.send_data(0x00)
        self.send_data(0x0F)

        self.send_command(0x45)  # Set RAM Y address
        self.send_data(0x27)
        self.send_data(0x01)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # Border waveform
        self.send_data(0x05)

        self.send_command(0x18)  # Temperature sensor
        self.send_data(0x80)

        self.send_command(0x4E)  # Set RAM X counter
        self.send_data(0x00)

        self.send_command(0x4F)  # Set RAM Y counter
        self.send_data(0x27)
        self.send_data(0x01)

        self.wait_until_idle()
        print("  ✅ Init abgeschlossen")

    def clear(self):
        """Lösche Display (komplett weiß)"""
        print("\n5. Lösche Display...")

        # Sende weiße Daten für Schwarz-Buffer
        self.send_command(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        # Sende weiße Daten für Rot-Buffer
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.turn_on_display()

    def display(self, black_image, red_image):
        """
        Zeige Bild an
        black_image: PIL Image für schwarz (1-bit)
        red_image: PIL Image für rot (1-bit)
        """
        print("\n6. Sende Bilddaten...")

        if black_image.mode != '1':
            black_image = black_image.convert('1')
        if red_image.mode != '1':
            red_image = red_image.convert('1')

        # Schwarz-Daten senden
        print("  Sende Schwarz-Buffer...")
        self.send_command(0x24)
        black_bytes = black_image.tobytes()
        for i in range(len(black_bytes)):
            self.send_data(black_bytes[i])  # NICHT invertieren

        # Rot-Daten senden
        print("  Sende Rot-Buffer...")
        self.send_command(0x26)
        red_bytes = red_image.tobytes()
        for i in range(len(red_bytes)):
            self.send_data(red_bytes[i])  # NICHT invertieren

        self.turn_on_display()

    def turn_on_display(self):
        """Display-Update aktivieren"""
        print("  Aktiviere Display-Update...")
        self.send_command(0x20)
        self.wait_until_idle()

    def sleep(self):
        """Sleep-Modus"""
        print("\n7. Sleep-Modus...")
        self.send_command(0x10)
        self.send_data(0x01)
        self.delay_ms(100)


def main():
    """Haupt-Test-Funktion"""
    print("="*60)
    print("MH-ET LIVE 2.9\" Display Test")
    print("GDEW029Z10 - Rot/Schwarz/Weiß")
    print("="*60)

    try:
        epd = GDEW029Z10()
        epd.init()

        # Clear Display
        epd.clear()

        print("\n8. Erstelle Test-Bild...")

        # Erstelle Bilder (128x296)
        black_img = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
        red_img = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, EPD_WIDTH-1, EPD_HEIGHT-1), outline=0, width=2)

        # Font laden
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        # Text in Schwarz
        draw_black.text((10, 20), "GPS", font=font_large, fill=0)
        draw_black.text((10, 70), "DEVICE", font=font_medium, fill=0)

        # Text in Rot
        draw_red.text((10, 120), "ANDY", font=font_large, fill=0)

        # Schwarzes Rechteck
        draw_black.rectangle((10, 180, 60, 220), fill=0)

        # Rotes Rechteck
        draw_red.rectangle((70, 180, 120, 220), fill=0)

        print("  ✅ Bild erstellt")

        # Anzeigen
        epd.display(black_img, red_img)

        # Sleep
        epd.sleep()

        print("\n" + "="*60)
        print("✅ TEST ERFOLGREICH!")
        print("="*60)
        print("\nDu solltest jetzt sehen:")
        print("  - Schwarzen Rahmen")
        print("  - 'GPS DEVICE' in SCHWARZ")
        print("  - 'ANDY' in ROT")
        print("  - Schwarzes + Rotes Rechteck")
        print("\nDas Bild bleibt auch beim Ausschalten sichtbar!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nTest abgebrochen")
        GPIO.cleanup()

    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
