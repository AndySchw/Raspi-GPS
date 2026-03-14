#!/usr/bin/env python3
"""
Test mit RAW-Bytes OHNE PIL
Erstelle Muster komplett manuell
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("RAW PATTERN TEST (ohne PIL)")
print("="*60)
print(f"Display: {EPD_WIDTH}x{EPD_HEIGHT}")
print(f"Bytes total: {int(EPD_WIDTH * EPD_HEIGHT / 8)}")
print(f"Bytes pro Zeile: {int(EPD_WIDTH / 8)}")
print("="*60)

# Bit-Reverse Lookup
BIT_REVERSE = [
    0x00, 0x80, 0x40, 0xC0, 0x20, 0xA0, 0x60, 0xE0,
    0x10, 0x90, 0x50, 0xD0, 0x30, 0xB0, 0x70, 0xF0,
    0x08, 0x88, 0x48, 0xC8, 0x28, 0xA8, 0x68, 0xE8,
    0x18, 0x98, 0x58, 0xD8, 0x38, 0xB8, 0x78, 0xF8,
    0x04, 0x84, 0x44, 0xC4, 0x24, 0xA4, 0x64, 0xE4,
    0x14, 0x94, 0x54, 0xD4, 0x34, 0xB4, 0x74, 0xF4,
    0x0C, 0x8C, 0x4C, 0xCC, 0x2C, 0xAC, 0x6C, 0xEC,
    0x1C, 0x9C, 0x5C, 0xDC, 0x3C, 0xBC, 0x7C, 0xFC,
    0x02, 0x82, 0x42, 0xC2, 0x22, 0xA2, 0x62, 0xE2,
    0x12, 0x92, 0x52, 0xD2, 0x32, 0xB2, 0x72, 0xF2,
    0x0A, 0x8A, 0x4A, 0xCA, 0x2A, 0xAA, 0x6A, 0xEA,
    0x1A, 0x9A, 0x5A, 0xDA, 0x3A, 0xBA, 0x7A, 0xFA,
    0x06, 0x86, 0x46, 0xC6, 0x26, 0xA6, 0x66, 0xE6,
    0x16, 0x96, 0x56, 0xD6, 0x36, 0xB6, 0x76, 0xF6,
    0x0E, 0x8E, 0x4E, 0xCE, 0x2E, 0xAE, 0x6E, 0xEE,
    0x1E, 0x9E, 0x5E, 0xDE, 0x3E, 0xBE, 0x7E, 0xFE,
    0x01, 0x81, 0x41, 0xC1, 0x21, 0xA1, 0x61, 0xE1,
    0x11, 0x91, 0x51, 0xD1, 0x31, 0xB1, 0x71, 0xF1,
    0x09, 0x89, 0x49, 0xC9, 0x29, 0xA9, 0x69, 0xE9,
    0x19, 0x99, 0x59, 0xD9, 0x39, 0xB9, 0x79, 0xF9,
    0x05, 0x85, 0x45, 0xC5, 0x25, 0xA5, 0x65, 0xE5,
    0x15, 0x95, 0x55, 0xD5, 0x35, 0xB5, 0x75, 0xF5,
    0x0D, 0x8D, 0x4D, 0xCD, 0x2D, 0xAD, 0x6D, 0xED,
    0x1D, 0x9D, 0x5D, 0xDD, 0x3D, 0xBD, 0x7D, 0xFD,
    0x03, 0x83, 0x43, 0xC3, 0x23, 0xA3, 0x63, 0xE3,
    0x13, 0x93, 0x53, 0xD3, 0x33, 0xB3, 0x73, 0xF3,
    0x0B, 0x8B, 0x4B, 0xCB, 0x2B, 0xAB, 0x6B, 0xEB,
    0x1B, 0x9B, 0x5B, 0xDB, 0x3B, 0xBB, 0x7B, 0xFB,
    0x07, 0x87, 0x47, 0xC7, 0x27, 0xA7, 0x67, 0xE7,
    0x17, 0x97, 0x57, 0xD7, 0x37, 0xB7, 0x77, 0xF7,
    0x0F, 0x8F, 0x4F, 0xCF, 0x2F, 0xAF, 0x6F, 0xEF,
    0x1F, 0x9F, 0x5F, 0xDF, 0x3F, 0xBF, 0x7F, 0xFF
]

class EPD_Raw:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

    def cmd(self, command):
        GPIO.output(DC_PIN, 0)
        GPIO.output(CS_PIN, 0)
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, 1)

    def data(self, data):
        GPIO.output(DC_PIN, 1)
        GPIO.output(CS_PIN, 0)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, 1)

    def reset(self):
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 0)
        time.sleep(0.02)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def init(self):
        print("\n1. Init Display...")
        self.reset()
        time.sleep(1)

        self.cmd(0x12)
        time.sleep(1)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)

        self.cmd(0x44)
        self.data([0x00, 0x24])

        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x18)
        self.data(0x80)

        self.cmd(0x4E)
        self.data(0x00)

        self.cmd(0x4F)
        self.data([0x00, 0x00])

        time.sleep(0.5)
        print("   ✅ Init OK")

    def show_stripes(self):
        """Zeige horizontale Streifen"""
        print("\n2. Sende HORIZONTALE STREIFEN...")

        bytes_per_line = int(EPD_WIDTH / 8)  # 37 Bytes pro Zeile
        total_lines = EPD_HEIGHT  # 128 Zeilen

        print(f"   {bytes_per_line} Bytes/Zeile, {total_lines} Zeilen")

        # Schwarz-Buffer: Streifen-Muster
        self.cmd(0x24)

        for line in range(total_lines):
            if line < 30:
                # Erste 30 Zeilen: komplett schwarz
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0x00])  # Schwarz
            elif line < 60:
                # Nächste 30 Zeilen: komplett weiß
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0xFF])  # Weiß
            elif line < 90:
                # Nächste 30 Zeilen: Streifenmuster
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0xAA])  # 10101010
            else:
                # Rest: Weiß
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0xFF])  # Weiß

        # Rot-Buffer: Rot-Streifen
        self.cmd(0x26)

        for line in range(total_lines):
            if line >= 95 and line < 125:
                # Zeilen 95-125: ROT
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0xFF])  # Rot
            else:
                # Rest: kein Rot
                for b in range(bytes_per_line):
                    self.data(BIT_REVERSE[0x00])  # Kein Rot

        print("   ✅ Daten gesendet")

        print("\n3. Update Display...")
        self.cmd(0x20)

        print("4. Warte 15 Sekunden...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n   ✅ Fertig!")

    def sleep(self):
        self.cmd(0x10)
        self.data(0x01)


try:
    print("\nTest: Manuelle Streifen-Muster (ohne PIL)")

    epd = EPD_Raw()
    epd.init()
    epd.show_stripes()
    epd.sleep()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN")
    print("="*60)
    print("\nDu solltest HORIZONTALE STREIFEN sehen:")
    print("  - Oben (Zeile 0-30): SCHWARZER Balken")
    print("  - Dann (Zeile 30-60): WEISSER Balken")
    print("  - Dann (Zeile 60-90): GESTREIFTER Balken (schwarz/weiß)")
    print("  - Unten (Zeile 95-125): ROTER Balken")
    print("\nSIND DIE STREIFEN HORIZONTAL oder VERTIKAL?")
    print("Und sind sie SAUBER oder gegrizel?")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
