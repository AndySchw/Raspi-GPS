#!/usr/bin/env python3
"""
Test: NUR Rot-Buffer nutzen
Theorie: Schwarz-Buffer funktioniert nicht
Lösung: Nutze Rot-Buffer für ALLES (Rot + kein Rot = Schwarz)
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

EPD_WIDTH = 128
EPD_HEIGHT = 296

print("="*60)
print("TEST: NUR ROT-BUFFER")
print("="*60)

class RedOnlyEPD:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

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

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def test_three_colors(self):
        """Teste 3 Farben: Weiß, Schwarz, Rot"""
        print("\n1. Test: Weiß, Schwarz, Rot...")
        self.reset()

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Schwarz-Buffer: Komplett auf 0x00 (schwarz)
        print("   Setze Schwarz-Buffer auf 0x00...")
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0x00)

        # Rot-Buffer: Streifen-Muster
        print("   Setze Rot-Buffer (Streifen)...")
        self.cmd(0x26)

        # Erste 1000 Bytes: 0x00 = ROT zeigen
        for i in range(1000):
            self.data(0x00)

        # Nächste 1000 Bytes: 0xFF = SCHWARZ zeigen (weil Schwarz-Buffer 0x00 ist)
        for i in range(1000):
            self.data(0xFF)

        # Rest: 0x00 = ROT
        for i in range(bytes_total - 2000):
            self.data(0x00)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)

        print("\n   >>> WAS SIEHST DU? <<<")
        print("   - ROT überall?")
        print("   - Oder ROT + SCHWARZER Streifen?")
        input("\n   [ENTER] für nächsten Test...")

    def test_black_buffer_variants(self):
        """Teste verschiedene Schwarz-Buffer Werte"""
        print("\n2. Test: Schwarz-Buffer Varianten...")

        variants = [
            (0x00, "0x00 (sollte schwarz sein)"),
            (0xFF, "0xFF (sollte weiß sein)"),
        ]

        for value, desc in variants:
            print(f"\n   Test: Schwarz-Buffer = {desc}")
            self.reset()

            bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

            # Schwarz-Buffer mit Test-Wert
            self.cmd(0x24)
            for i in range(bytes_total):
                self.data(value)

            # Rot-Buffer: Hälfte Rot, Hälfte kein Rot
            self.cmd(0x26)
            half = bytes_total // 2

            # Erste Hälfte: 0x00 = Rot
            for i in range(half):
                self.data(0x00)

            # Zweite Hälfte: 0xFF = kein Rot
            for i in range(bytes_total - half):
                self.data(0xFF)

            self.cmd(0x20)
            print("      Warte 10 Sekunden...")
            time.sleep(10)

            print(f"\n      >>> Schwarz-Buffer: {desc} <<<")
            print("      Was siehst du?")
            response = input("      Beschreibe kurz: ")

    def test_init_commands(self):
        """Teste spezielle Init-Befehle"""
        print("\n3. Test: Mit Init-Befehlen...")
        self.reset()

        # Versuche Panel Setting (0x00) mit verschiedenen Werten
        print("   Sende Panel Setting 0x00...")
        self.cmd(0x00)
        self.data(0xbf)  # 3-color mode aktivieren

        time.sleep(0.5)

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Schwarz-Buffer: Muster
        self.cmd(0x24)
        for i in range(1000):
            self.data(0x00)  # Schwarz
        for i in range(bytes_total - 1000):
            self.data(0xFF)  # Weiß

        # Rot-Buffer: Andere Position
        self.cmd(0x26)
        for i in range(500):
            self.data(0xFF)
        for i in range(500):
            self.data(0x00)  # Rot
        for i in range(bytes_total - 1000):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)

        print("\n   >>> Mit Panel Setting <<<")
        print("   Siehst du jetzt SCHWARZ + ROT?")


try:
    print("\n⚠️  Versuche herauszufinden warum nur Rot angezeigt wird!\n")

    epd = RedOnlyEPD()
    epd.test_three_colors()
    epd.test_black_buffer_variants()
    epd.test_init_commands()

    print("\n" + "="*60)
    print("TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWelcher Test hat SCHWARZ gezeigt?")
    print("="*60)

    GPIO.cleanup()

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
