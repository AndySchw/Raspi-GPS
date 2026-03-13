#!/usr/bin/env python3
"""
Display-Test mit korrigierter Byte-Order und Rotation
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8

EPD_WIDTH = 128
EPD_HEIGHT = 296

class EPD_Fixed:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000  # Langsameres SPI

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        GPIO.output(CS_PIN, 0)
        self.spi.xfer2([c])
        GPIO.output(CS_PIN, 1)

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        GPIO.output(CS_PIN, 0)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)
        GPIO.output(CS_PIN, 1)

    def init(self):
        print("Init...")
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 0)
        time.sleep(0.02)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)

        self.cmd(0x44)
        self.data([0x00, 0x0F])

        self.cmd(0x45)
        self.data([0x27, 0x01, 0x00, 0x00])

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x21)
        self.data(0x00)

        self.cmd(0x18)
        self.data(0x80)

        print("Init OK")

    def display_simple(self):
        """Einfaches Testmuster ohne PIL"""
        print("\nZeige einfaches Muster...")

        # Position setzen
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Schwarz-Buffer: Hälfte schwarz, Hälfte weiß
        print("  Schwarz-Buffer...")
        self.cmd(0x24)
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        half = bytes_total // 2

        for i in range(half):
            self.data(0x00)  # Erste Hälfte: schwarz
        for i in range(bytes_total - half):
            self.data(0xFF)  # Zweite Hälfte: weiß

        # Rot-Buffer: komplett leer
        print("  Rot-Buffer...")
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0x00)  # Kein Rot

        # Update
        print("  Update...")
        self.cmd(0x20)

        print("  Warte 20 Sekunden...")
        for i in range(20, 0, -1):
            print(f"    {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n  ✅ Sollte halb schwarz, halb weiß sein!")

    def display_red_test(self):
        """Nur Rot-Test"""
        print("\nZeige ROT-Test...")

        # Position setzen
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Schwarz-Buffer: komplett weiß
        print("  Schwarz-Buffer (leer)...")
        self.cmd(0x24)
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        for i in range(bytes_total):
            self.data(0xFF)

        # Rot-Buffer: Hälfte rot
        print("  Rot-Buffer (halb voll)...")
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        half = bytes_total // 2
        for i in range(half):
            self.data(0xFF)  # Erste Hälfte: rot
        for i in range(bytes_total - half):
            self.data(0x00)  # Zweite Hälfte: kein Rot

        # Update
        print("  Update...")
        self.cmd(0x20)

        print("  Warte 20 Sekunden...")
        for i in range(20, 0, -1):
            print(f"    {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n  ✅ Sollte halb rot, halb weiß sein!")


print("="*60)
print("DISPLAY-TEST MIT FIXEN")
print("="*60)
print("\n⚠️  BUSY-Pin (Lila) muss ABGEZOGEN sein!")

try:
    epd = EPD_Fixed()
    epd.init()
    time.sleep(1)

    print("\n" + "="*60)
    print("TEST 1: Schwarz/Weiß Hälfte")
    print("="*60)
    epd.display_simple()

    time.sleep(3)

    print("\n" + "="*60)
    print("TEST 2: Rot/Weiß Hälfte")
    print("="*60)
    epd.display_red_test()

    print("\n" + "="*60)
    print("✅ TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWas hast du gesehen?")
    print("  Test 1: Sollte eine Hälfte schwarz, eine weiß sein")
    print("  Test 2: Sollte eine Hälfte rot, eine weiß sein")
    print("="*60)

except Exception as e:
    print(f"\nFehler: {e}")
    import traceback
    traceback.print_exc()
finally:
    GPIO.cleanup()
