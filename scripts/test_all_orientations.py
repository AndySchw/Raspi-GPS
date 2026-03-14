#!/usr/bin/env python3
"""
Teste ALLE möglichen Orientierungen und Byte-Orders
Um herauszufinden welche Kombination funktioniert
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("="*60)
print("ORIENTIERUNGS-TEST - Alle Kombinationen")
print("="*60)

class OrientationTest:
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
        time.sleep(0.02)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def init_gxepd2(self):
        """GxEPD2 Init"""
        self.reset()
        self.wait_busy()

        self.cmd(0x01)  # Power Setting
        self.data([0x03, 0x00, 0x2b, 0x2b, 0x09])

        self.cmd(0x06)  # Booster Soft Start
        self.data([0x17, 0x17, 0x17])

        self.cmd(0x04)  # Power On
        self.wait_busy()

        self.cmd(0x00)  # Panel Setting
        self.data(0xbf)

        self.cmd(0x30)  # PLL
        self.data(0x3a)

        self.cmd(0x61)  # Resolution
        self.data([0x80, 0x01, 0x28])  # 128x296

        self.cmd(0x82)  # VCM
        self.data(0x12)

        self.cmd(0x50)  # VCOM
        self.data(0x97)

    def test_simple_pattern(self, width, height, label):
        """Zeige einfaches Muster"""
        print(f"\n>>> TEST: {label} <<<")
        print(f"    Auflösung: {width}x{height}")

        bytes_total = int(width * height / 8)
        print(f"    Bytes total: {bytes_total}")

        # BW RAM - Streifen-Muster
        self.cmd(0x10)

        # Erste 200 Bytes SCHWARZ
        for i in range(200):
            self.data(0x00)

        # Nächste 200 Bytes WEISS
        for i in range(200):
            self.data(0xFF)

        # Rest WEISS
        for i in range(bytes_total - 400):
            self.data(0xFF)

        # RED RAM - Rote Box
        self.cmd(0x13)

        # Erste 600 Bytes kein Rot
        for i in range(600):
            self.data(0x00)

        # Nächste 200 Bytes ROT
        for i in range(200):
            self.data(0xFF)

        # Rest kein Rot
        for i in range(bytes_total - 800):
            self.data(0x00)

        # Update
        self.cmd(0x12)
        self.wait_busy()

        print("    Warte 3 Sekunden...")
        time.sleep(3)
        print("    Was siehst du?")
        print("    - Wo ist SCHWARZ?")
        print("    - Wo ist ROT?")
        input("    [ENTER] für nächsten Test...")


try:
    test = OrientationTest()

    print("\n⚠️  WICHTIG: Notiere bei jedem Test WO die Farben sind!")
    print("    (oben/unten/links/rechts)\n")

    input("[ENTER] um zu starten...")

    # Test 1: 128x296 (GxEPD2 Standard)
    test.init_gxepd2()
    test.test_simple_pattern(128, 296, "128x296 (Hochformat)")

    # Test 2: 296x128 (Querformat)
    test.reset()
    test.wait_busy()

    test.cmd(0x01)
    test.data([0x03, 0x00, 0x2b, 0x2b, 0x09])

    test.cmd(0x06)
    test.data([0x17, 0x17, 0x17])

    test.cmd(0x04)
    test.wait_busy()

    test.cmd(0x00)
    test.data(0xbf)

    test.cmd(0x30)
    test.data(0x3a)

    # GEÄNDERTE AUFLÖSUNG!
    test.cmd(0x61)
    test.data([0x01, 0x28, 0x80])  # 296x128 statt 128x296

    test.cmd(0x82)
    test.data(0x12)

    test.cmd(0x50)
    test.data(0x97)

    test.test_simple_pattern(296, 128, "296x128 (Querformat)")

    # Deep Sleep
    test.cmd(0x02)
    test.wait_busy()
    test.cmd(0x07)
    test.data(0xA5)

    print("\n" + "="*60)
    print("TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWelcher Test hat die Farben RICHTIG angezeigt?")
    print("  Test 1 (128x296) oder Test 2 (296x128)?")
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
