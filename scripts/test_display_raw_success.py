#!/usr/bin/env python3
"""
Test: Genau wie Test 1 der funktioniert hat!
ROH-BYTES statt PIL
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("="*60)
print("RAW BYTES TEST - wie Test 1!")
print("="*60)

class RawSuccess:
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

    def show_pattern(self):
        """Genau wie Test 1: Schwarz mit roten Streifen"""
        print("\n1. Erstelle Muster (ROH-BYTES)...")
        self.reset()

        # 296x128 = 37888 bits = 4736 bytes
        bytes_total = 4736
        bytes_per_line = 37  # 296 / 8

        # Schwarz-Buffer: Komplett schwarz
        print("   Schwarz-Buffer: 0x00 (komplett schwarz)...")
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0x00)

        # Rot-Buffer: Vertikale Streifen
        print("   Rot-Buffer: Streifen-Muster...")
        self.cmd(0x26)

        # Erstelle 3 vertikale rote Streifen
        for line in range(128):  # 128 Zeilen
            for col in range(bytes_per_line):  # 37 Bytes pro Zeile
                # Rote Streifen bei bestimmten Positionen
                if col in [5, 6, 15, 16, 25, 26]:
                    self.data(0x00)  # Rot
                else:
                    self.data(0xFF)  # Kein Rot (= schwarz vom anderen Buffer)

        self.cmd(0x20)
        print("\n2. Update Display...")
        time.sleep(10)

        print("\n   ✅ Fertig!")
        print("\n   Du solltest sehen:")
        print("   - SCHWARZER Hintergrund")
        print("   - 3 ROTE vertikale Streifen")


try:
    print("\n⚠️  Nutzt ROH-BYTES statt PIL!\n")

    epd = RawSuccess()
    epd.show_pattern()

    print("\n" + "="*60)
    print("SIEHST DU SCHWARZ + ROTE STREIFEN?")
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
