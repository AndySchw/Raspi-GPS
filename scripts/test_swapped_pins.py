#!/usr/bin/env python3
"""
TEST: RST und BUSY GETAUSCHT!
Verdacht: Die Pins sind am Display vertauscht
"""

import time
import spidev
import RPi.GPIO as GPIO

# GETAUSCHT!
RST_PIN = 17   # War vorher 24
BUSY_PIN = 24  # War vorher 17
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TEST MIT GETAUSCHTEN RST/BUSY PINS")
print("="*60)
print(f"RST:  GPIO{RST_PIN}  (war vorher GPIO24)")
print(f"BUSY: GPIO{BUSY_PIN}  (war vorher GPIO17)")
print("="*60)

class TestSwapped:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)

    def wait_busy(self):
        print(f"   BUSY vor Wait: {GPIO.input(BUSY_PIN)}")
        timeout = 0
        while GPIO.input(BUSY_PIN) == 0:
            time.sleep(0.01)
            timeout += 1
            if timeout > 2000:
                print("   TIMEOUT!")
                return
        print(f"   BUSY nach Wait: {GPIO.input(BUSY_PIN)}")

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def test_clear(self):
        print("\n1. Test: Clear White mit GETAUSCHTEN Pins!")
        self.reset()
        self.wait_busy()

        self.cmd(0x12)
        time.sleep(0.3)
        self.wait_busy()

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

        self.wait_busy()
        print("   ✅ Init OK")

        # Clear white
        print("\n2. Sende White-Buffer...")
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        print("\n3. Update Display...")
        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte WEISS sein!")

try:
    epd = TestSwapped()
    epd.test_clear()

    print("\n" + "="*60)
    print("Ist das Display WEISS?")
    print("Wenn JA -> RST/BUSY waren VERTAUSCHT!")
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
