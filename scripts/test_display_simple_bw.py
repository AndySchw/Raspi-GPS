#!/usr/bin/env python3
"""
Einfacher Schwarz/Weiß Test für GDEW029Z10
Testet nur den Schwarz-Buffer, Rot-Buffer bleibt leer
"""

import sys
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Pin-Definitionen
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

EPD_WIDTH = 128
EPD_HEIGHT = 296

class SimpleEPD:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000

    def send_command(self, command):
        GPIO.output(DC_PIN, GPIO.LOW)
        GPIO.output(CS_PIN, GPIO.LOW)
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, GPIO.HIGH)

    def send_data(self, data):
        GPIO.output(DC_PIN, GPIO.HIGH)
        GPIO.output(CS_PIN, GPIO.LOW)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, GPIO.HIGH)

    def wait_busy(self):
        print("  Warte...", end='', flush=True)
        while GPIO.input(BUSY_PIN) == GPIO.LOW:
            time.sleep(0.1)
        print(" OK")

    def reset(self):
        print("Reset...")
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)

    def init(self):
        print("Init...")
        self.reset()
        self.wait_busy()

        self.send_command(0x12)  # SWRESET
        self.wait_busy()

        self.send_command(0x01)  # Driver output
        self.send_data([0x27, 0x01, 0x00])

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.send_command(0x44)  # Set RAM X
        self.send_data([0x00, 0x0F])

        self.send_command(0x45)  # Set RAM Y
        self.send_data([0x27, 0x01, 0x00, 0x00])

        self.send_command(0x3C)  # Border
        self.send_data(0x05)

        self.send_command(0x18)  # Temperature
        self.send_data(0x80)

        self.send_command(0x4E)  # Set X counter
        self.send_data(0x00)

        self.send_command(0x4F)  # Set Y counter
        self.send_data([0x27, 0x01])

        self.wait_busy()
        print("Init OK")

    def clear_white(self):
        """Komplett weiß"""
        print("\nMache Display WEISS...")

        # Schwarz-Buffer: alles auf 0xFF (weiß)
        self.send_command(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        # Rot-Buffer: alles auf 0x00 (kein Rot)
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0x00)

        self.send_command(0x20)  # Update
        self.wait_busy()
        print("Sollte jetzt WEISS sein!")

    def clear_black(self):
        """Komplett schwarz"""
        print("\nMache Display SCHWARZ...")

        # Schwarz-Buffer: alles auf 0x00 (schwarz)
        self.send_command(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0x00)

        # Rot-Buffer: alles auf 0x00 (kein Rot)
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0x00)

        self.send_command(0x20)  # Update
        self.wait_busy()
        print("Sollte jetzt SCHWARZ sein!")

    def clear_red(self):
        """Komplett rot (zum Testen)"""
        print("\nMache Display ROT...")

        # Schwarz-Buffer: alles auf 0xFF (weiß = kein Schwarz)
        self.send_command(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        # Rot-Buffer: alles auf 0xFF (rot)
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x20)  # Update
        self.wait_busy()
        print("Sollte jetzt ROT sein!")

    def test_pattern(self):
        """Testmuster: Streifen"""
        print("\nZeige Testmuster...")

        # Schwarz-Buffer: Streifen
        self.send_command(0x24)
        for row in range(self.height):
            for col in range(int(self.width / 8)):
                if row < 100:
                    self.send_data(0xAA)  # Muster
                else:
                    self.send_data(0xFF)  # Weiß

        # Rot-Buffer: leer
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0x00)

        self.send_command(0x20)
        self.wait_busy()
        print("Sollte Streifenmuster oben zeigen!")

    def sleep(self):
        self.send_command(0x10)
        self.send_data(0x01)


print("="*60)
print("EINFACHER DISPLAY-TEST")
print("="*60)

try:
    epd = SimpleEPD()
    epd.init()

    print("\n>>> TEST 1: Komplett WEISS <<<")
    epd.clear_white()
    time.sleep(3)

    print("\n>>> TEST 2: Komplett SCHWARZ <<<")
    epd.clear_black()
    time.sleep(3)

    print("\n>>> TEST 3: Komplett ROT (Test) <<<")
    epd.clear_red()
    time.sleep(3)

    print("\n>>> TEST 4: Testmuster (Streifen) <<<")
    epd.test_pattern()
    time.sleep(3)

    epd.sleep()

    print("\n" + "="*60)
    print("Tests abgeschlossen!")
    print("Welche Farben hast du gesehen?")
    print("="*60)

except Exception as e:
    print(f"Fehler: {e}")
    import traceback
    traceback.print_exc()
finally:
    GPIO.cleanup()
