#!/usr/bin/env python3
"""
Test: KORREKTE INIT-SEQUENZ
Problem: Daten kommen schräg an
Lösung: Data Entry Mode und RAM-Adressierung korrigieren
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("="*60)
print("INIT-SEQUENZ FIX")
print("="*60)

class InitFix:
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

    def wait_busy(self):
        timeout = 0
        while GPIO.input(BUSY_PIN) == 0:
            time.sleep(0.01)
            timeout += 1
            if timeout > 2000:
                return

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def init_full(self):
        """Vollständige Init-Sequenz mit ALLEN Befehlen"""
        print("\n1. Vollständige Init...")
        self.reset()
        self.wait_busy()

        # Software Reset
        self.cmd(0x12)
        time.sleep(0.3)
        self.wait_busy()

        # Driver Output Control (0x01)
        # Definiert die Anzahl der Zeilen
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen (0x0127 = 295+1)

        # Data Entry Mode (0x11) - WICHTIG!
        # Bit 0-1: Adress-Richtung (00=Y dec X dec, 01=Y dec X inc, 10=Y inc X dec, 11=Y inc X inc)
        # Bit 2: AM (Address Mode) 0=X, 1=Y
        self.cmd(0x11)
        self.data(0x03)  # Y inc, X inc

        # Set RAM X Address Start/End (0x44)
        self.cmd(0x44)
        self.data([0x00, 0x0F])  # 0 bis 15 (16 bytes = 128 pixel)

        # Set RAM Y Address Start/End (0x45)
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])  # 0 bis 295

        # Border Waveform Control (0x3C)
        self.cmd(0x3C)
        self.data(0x05)  # Follow LUT

        # Temperature Sensor (0x18)
        self.cmd(0x18)
        self.data(0x80)  # Internal sensor

        # Set RAM X Address Counter (0x4E)
        self.cmd(0x4E)
        self.data(0x00)  # Start bei 0

        # Set RAM Y Address Counter (0x4F)
        self.cmd(0x4F)
        self.data([0x00, 0x00])  # Start bei 0

        self.wait_busy()
        print("   ✅ Init OK")

    def test_simple_blocks(self):
        """Teste einfache Blöcke"""
        print("\n2. Teste einfache Blöcke...")

        bytes_total = 4736  # 128x296 / 8

        # Schwarz-Buffer: Erste 1000 Bytes schwarz, Rest weiß
        self.cmd(0x24)
        for i in range(1000):
            self.data(0x00)  # Schwarz
        for i in range(bytes_total - 1000):
            self.data(0xFF)  # Weiß

        # Rot-Buffer: Bytes 1000-2000 rot, Rest transparent
        self.cmd(0x26)
        for i in range(1000):
            self.data(0xFF)  # Kein Rot
        for i in range(1000):
            self.data(0x00)  # Rot
        for i in range(bytes_total - 2000):
            self.data(0xFF)  # Kein Rot

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)

        print("\n   >>> SCHAU AUFS DISPLAY <<<")
        print("   Du solltest sehen:")
        print("   - Einen SCHWARZEN Block")
        print("   - Einen ROTEN Block")
        print("   - Weißen Rest")
        print("\n   Sind die Blöcke GERADE (nicht schräg)?")


try:
    print("\n⚠️  Vollständige Init-Sequenz!\n")

    epd = InitFix()
    epd.init_full()
    epd.test_simple_blocks()

    print("\n" + "="*60)
    print("Sind die Blöcke GERADE oder immer noch schräg?")
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
