#!/usr/bin/env python3
"""
LETZTER VERSUCH: Buffer-Kombination
Theorie: Schwarz = BEIDE Buffer auf 0x00
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("="*60)
print("COMBINED BUFFERS TEST")
print("="*60)

class CombinedTest:
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

    def init(self):
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
        self.data([0x00, 0x0F])
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])
        self.cmd(0x3C)
        self.data(0x05)
        self.cmd(0x18)
        self.data(0x80)
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])
        self.wait_busy()

    def test_color_combinations(self):
        """Teste alle Farb-Kombinationen"""
        print("\n1. TESTE FARB-KOMBINATIONEN...")
        print("="*60)

        bytes_total = 4736
        tests = [
            # (Schwarz-Wert, Rot-Wert, Beschreibung)
            (0xFF, 0xFF, "Beide 0xFF - sollte WEISS sein"),
            (0x00, 0xFF, "Schwarz=0x00, Rot=0xFF"),
            (0xFF, 0x00, "Schwarz=0xFF, Rot=0x00 - sollte ROT sein"),
            (0x00, 0x00, "Beide 0x00 - sollte SCHWARZ sein?"),
        ]

        for black_val, red_val, desc in tests:
            print(f"\nTest: {desc}")
            print(f"  Schwarz-Buffer: 0x{black_val:02X}")
            print(f"  Rot-Buffer: 0x{red_val:02X}")

            self.init()

            # Schwarz-Buffer
            self.cmd(0x24)
            for i in range(bytes_total):
                self.data(black_val)

            # Rot-Buffer
            self.cmd(0x26)
            for i in range(bytes_total):
                self.data(red_val)

            self.cmd(0x20)
            print("  Warte 8 Sekunden...")
            time.sleep(8)

            response = input(f"\n  >>> Welche FARBE siehst du? ")
            print(f"  Antwort: {response}")

        print("\n" + "="*60)
        print("ZUSAMMENFASSUNG:")
        print("="*60)
        print("Welche Kombination ergab welche Farbe?")
        print("  0xFF/0xFF = ?")
        print("  0x00/0xFF = ?")
        print("  0xFF/0x00 = ?")
        print("  0x00/0x00 = ?")


try:
    print("\n⚠️  Testet ALLE Farb-Kombinationen!")
    print("    So finden wir heraus wie die Buffer arbeiten!\n")

    epd = CombinedTest()
    epd.test_color_combinations()

    print("\n" + "="*60)
    print("JETZT WISSEN WIR WIE DIE BUFFER FUNKTIONIEREN!")
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
