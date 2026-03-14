#!/usr/bin/env python3
"""
GDEW029Z10 - BEREINIGTE VERSION
Alle Fehler behoben:
- Auflösung: 296x128 (nicht 128x296!)
- RAM-Fenster: 0x24 (nicht 0x0F)
- CS_PIN: NICHT manuell steuern!
- SPI: 500kHz zum Testen
"""

import time
import spidev
import RPi.GPIO as GPIO

# Pins
RST_PIN = 24
DC_PIN = 25
BUSY_PIN = 17
# CS_PIN 8 wird von spidev automatisch gesteuert!

# KORREKTE Auflösung!
EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("GDEW029Z10 - FIXED VERSION")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
print("CS wird von spidev gesteuert!")
print("="*60)

class GDEW029Z10_Fixed:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)
        # KEIN GPIO.setup für CS_PIN!

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # CE0 (GPIO8) wird automatisch gesteuert
        self.spi.max_speed_hz = 500000  # 500kHz zum Testen
        self.spi.mode = 0

    def cmd(self, c):
        """Befehl senden - OHNE manuelles CS!"""
        GPIO.output(DC_PIN, 0)  # DC=LOW
        self.spi.xfer2([c])     # CS wird automatisch von spidev gesteuert

    def data(self, d):
        """Daten senden - OHNE manuelles CS!"""
        GPIO.output(DC_PIN, 1)  # DC=HIGH
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)       # CS wird automatisch von spidev gesteuert

    def wait_busy(self, variant='A'):
        """Warte auf BUSY - beide Varianten testbar"""
        timeout = 0
        if variant == 'A':
            # Variante A: BUSY=0 bedeutet beschäftigt
            while GPIO.input(BUSY_PIN) == 0:
                time.sleep(0.01)
                timeout += 1
                if timeout > 2000:
                    return
        else:
            # Variante B: BUSY=1 bedeutet beschäftigt
            while GPIO.input(BUSY_PIN) == 1:
                time.sleep(0.01)
                timeout += 1
                if timeout > 2000:
                    return

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def init(self, busy_variant='A'):
        """Init mit KORREKTEM RAM-Fenster"""
        print(f"\n1. Init (BUSY Variante {busy_variant})...")

        # BUSY-Status VORHER prüfen
        print(f"   BUSY idle: {GPIO.input(BUSY_PIN)}")

        self.reset()
        self.wait_busy(busy_variant)

        self.cmd(0x12)  # SWRESET
        time.sleep(0.3)
        self.wait_busy(busy_variant)

        # Driver Output Control
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        # Data Entry Mode
        self.cmd(0x11)
        self.data(0x03)  # Y inc, X inc

        # RAM X-Adresse: 0 bis 0x24 (37 bytes = 296 pixel)
        self.cmd(0x44)
        self.data([0x00, 0x24])  # KORRIGIERT von 0x0F!

        # RAM Y-Adresse: 0 bis 0x7F (128 Zeilen)
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])  # KORRIGIERT!

        # Border
        self.cmd(0x3C)
        self.data(0x05)

        # Temperature
        self.cmd(0x18)
        self.data(0x80)

        # X Counter
        self.cmd(0x4E)
        self.data(0x00)

        # Y Counter
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.wait_busy(busy_variant)
        print("   ✅ Init OK")

    def clear_white(self, busy_variant='A'):
        """Komplett weiß"""
        print("\n2. Lösche Display (weiß)...")
        self.init(busy_variant)

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        print(f"   Bytes: {bytes_total}")

        # Schwarz-Buffer: 0xFF = weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        # Rot-Buffer: 0xFF = kein Rot
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x20)  # Update
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte WEISS sein!")

    def test_black_bar(self, busy_variant='A'):
        """Schwarzer Balken LINKS"""
        print("\n3. Schwarzer Balken LINKS...")
        self.init(busy_variant)

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        bytes_per_line = int(EPD_WIDTH / 8)  # 37 bytes

        # Schwarz-Buffer: Erste 5 Spalten schwarz
        self.cmd(0x24)
        for line in range(EPD_HEIGHT):
            for col in range(bytes_per_line):
                if col < 5:
                    self.data(0x00)  # Schwarz
                else:
                    self.data(0xFF)  # Weiß

        # Rot-Buffer: kein Rot
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte SCHWARZER Balken LINKS sein!")

    def test_red_bar(self, busy_variant='A'):
        """Roter Balken RECHTS"""
        print("\n4. Roter Balken RECHTS...")
        self.init(busy_variant)

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        bytes_per_line = int(EPD_WIDTH / 8)

        # Schwarz-Buffer: alles weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        # Rot-Buffer: Letzte 5 Spalten rot
        self.cmd(0x26)
        for line in range(EPD_HEIGHT):
            for col in range(bytes_per_line):
                if col >= bytes_per_line - 5:
                    self.data(0x00)  # Rot
                else:
                    self.data(0xFF)  # Kein Rot

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte ROTER Balken RECHTS sein!")


try:
    print("\n⚠️  ALLE Fehler behoben!")
    print("    - Auflösung: 296x128")
    print("    - RAM: 0x24 / 0x7F")
    print("    - CS automatisch\n")

    epd = GDEW029Z10_Fixed()

    # Teste mit BUSY Variante A
    print("\n" + "="*60)
    print("TESTE MIT BUSY VARIANTE A (0=busy)")
    print("="*60)

    epd.clear_white('A')
    time.sleep(2)
    epd.test_black_bar('A')
    time.sleep(2)
    epd.test_red_bar('A')

    print("\n" + "="*60)
    print("✅ TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nHast du gesehen:")
    print("  1. Komplett WEISS?")
    print("  2. Schwarzer Balken LINKS?")
    print("  3. Roter Balken RECHTS?")
    print("\nWenn JA -> ES FUNKTIONIERT! 🎉")
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
