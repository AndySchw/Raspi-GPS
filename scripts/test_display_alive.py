#!/usr/bin/env python3
"""
Minimalster Test: Ist das Display noch am Leben?
Testet alle möglichen Befehls-Kombinationen
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8

print("="*60)
print("DISPLAY ALIVE TEST")
print("="*60)

class MinimalTest:
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
        print("1. Hardware Reset...")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def test_update_commands(self):
        """Teste verschiedene Update-Befehle"""
        self.reset()

        print("\n2. Teste Update-Befehl 0x12 (IL0373)...")
        self.cmd(0x12)
        print("   Warte 5 Sekunden...")
        time.sleep(5)
        print("   Siehst du FLACKERN? (ja/nein)")

        print("\n3. Teste Update-Befehl 0x20 (Standard)...")
        self.cmd(0x20)
        print("   Warte 5 Sekunden...")
        time.sleep(5)
        print("   Siehst du FLACKERN? (ja/nein)")

        print("\n4. Teste Clear-Screen-Muster...")

        # Versuche verschiedene RAM-Befehle
        print("   Versuche 0x10 (BW RAM)...")
        self.cmd(0x10)
        for i in range(100):
            self.data(0x00)  # Schwarz

        print("   Versuche 0x24 (alternativer RAM)...")
        self.cmd(0x24)
        for i in range(100):
            self.data(0x00)  # Schwarz

        print("   Versuche 0x13 (RED RAM)...")
        self.cmd(0x13)
        for i in range(100):
            self.data(0xFF)  # Rot

        print("   Versuche 0x26 (alternativer RED RAM)...")
        self.cmd(0x26)
        for i in range(100):
            self.data(0xFF)  # Rot

        print("\n5. Sende Update 0x12...")
        self.cmd(0x12)
        time.sleep(5)

        print("\n6. Sende Update 0x20...")
        self.cmd(0x20)
        time.sleep(5)

        print("\n7. Power-Befehle testen...")

        # Power ON (IL0373)
        print("   Power ON (0x04)...")
        self.cmd(0x04)
        time.sleep(1)

        # Nochmal Update
        print("   Update (0x12)...")
        self.cmd(0x12)
        time.sleep(5)

        print("\n" + "="*60)
        print("TEST ABGESCHLOSSEN")
        print("="*60)
        print("\nHat das Display irgendwann GEFLACKERT?")
        print("Wenn NEIN -> Display evtl. defekt oder falscher Controller")
        print("="*60)


try:
    print("\n⚠️  Dieser Test sendet verschiedene Befehle")
    print("    Achte auf FLACKERN am Display!\n")

    test = MinimalTest()
    test.test_update_commands()

    GPIO.cleanup()

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
