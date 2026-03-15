#!/usr/bin/env python3
"""
TESTE DOPPELTE RAM-BESCHREIBUNG

Problem: Während des Flackerns ist das RICHTIGE Bild da,
         danach wird es überschrieben!

Hypothese: Das Display hat TWO RAM-Areas:
- 0x24 = BLACK RAM (NEW)
- 0x26 = RED RAM (NEW)

ABER es gibt möglicherweise auch:
- 0x10 = BLACK RAM (OLD)
- 0x13 = RED RAM (OLD)

Oder wir müssen die Daten ZWEIMAL schreiben (vor UND nach Update)!
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TESTE DOPPELTE RAM-BESCHREIBUNG")
print("="*60)

class DoubleBufferTester:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.01)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.01)

    def init(self):
        """Standard Init"""
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

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

        time.sleep(0.2)

    def create_box_data(self):
        """Erstelle Daten für große schwarze Box"""
        data = []
        for y in range(128):
            for x_byte in range(37):
                # Große Box: Y 20-108, X-Byte 5-32
                if 20 <= y < 108 and 5 <= x_byte < 32:
                    data.append(0x00)  # Schwarz
                else:
                    data.append(0xFF)  # Weiß
        return data

    def test_1_normal(self):
        """Normal: Nur 0x24 und 0x26"""
        print("\n=== TEST 1: NORMAL (nur 0x24 + 0x26) ===")

        box_data = self.create_box_data()

        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        self.cmd(0x20)
        time.sleep(5)

    def test_2_write_twice(self):
        """Schreibe die Daten ZWEIMAL (vor Update)"""
        print("\n=== TEST 2: DATEN ZWEIMAL SCHREIBEN ===")

        box_data = self.create_box_data()

        # Erstes Mal
        print("   Schreibe Daten (1. Mal)...")
        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        # Pointer zurücksetzen
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Zweites Mal
        print("   Schreibe Daten (2. Mal)...")
        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        self.cmd(0x20)
        time.sleep(5)

    def test_3_use_old_ram(self):
        """Nutze 0x10 und 0x13 (OLD RAM) statt 0x24 und 0x26"""
        print("\n=== TEST 3: OLD RAM (0x10 + 0x13) ===")

        box_data = self.create_box_data()

        self.cmd(0x10)  # OLD Black RAM
        for byte in box_data:
            self.data(byte)

        self.cmd(0x13)  # OLD Red RAM
        for _ in box_data:
            self.data(0xFF)

        self.cmd(0x20)
        time.sleep(5)

    def test_4_both_rams(self):
        """Schreibe in BEIDE RAMs (OLD und NEW)"""
        print("\n=== TEST 4: BEIDE RAMs (0x10 + 0x24 + 0x13 + 0x26) ===")

        box_data = self.create_box_data()

        # OLD Black RAM
        print("   Schreibe OLD Black RAM (0x10)...")
        self.cmd(0x10)
        for byte in box_data:
            self.data(byte)

        # NEW Black RAM
        print("   Schreibe NEW Black RAM (0x24)...")
        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        # OLD Red RAM
        print("   Schreibe OLD Red RAM (0x13)...")
        self.cmd(0x13)
        for _ in box_data:
            self.data(0xFF)

        # NEW Red RAM
        print("   Schreibe NEW Red RAM (0x26)...")
        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        self.cmd(0x20)
        time.sleep(5)

    def test_5_write_after_update(self):
        """Schreibe NACH dem Update nochmal!"""
        print("\n=== TEST 5: NACH UPDATE NOCHMAL SCHREIBEN ===")

        box_data = self.create_box_data()

        # VOR Update
        print("   Schreibe VOR Update...")
        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        # Update
        print("   Update...")
        self.cmd(0x20)
        time.sleep(3)

        # NACH Update nochmal schreiben!
        print("   Schreibe NACH Update nochmal...")
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x24)
        for byte in box_data:
            self.data(byte)

        self.cmd(0x26)
        for _ in box_data:
            self.data(0xFF)

        # Zweites Update
        print("   Zweites Update...")
        self.cmd(0x20)
        time.sleep(3)


if __name__ == "__main__":
    print("\n⚠️  Dieser Test probiert verschiedene RAM-Schreib-Strategien")
    print("\nWir suchen den Modus, bei dem die schwarze Box")
    print("auch NACH dem Flackern noch sichtbar bleibt!")
    print("="*60)

    try:
        tester = DoubleBufferTester()

        tests = [
            ("Normal", tester.test_1_normal),
            ("Daten zweimal schreiben", tester.test_2_write_twice),
            ("OLD RAM (0x10/0x13)", tester.test_3_use_old_ram),
            ("BEIDE RAMs", tester.test_4_both_rams),
            ("Nach Update nochmal schreiben", tester.test_5_write_after_update)
        ]

        for i, (name, test_func) in enumerate(tests, 1):
            print(f"\n\n{'='*60}")
            print(f"TEST {i}/5: {name}")
            print(f"{'='*60}")

            tester.init()
            test_func()

            print("\n>>> ENDERGEBNIS <<<")
            print("Ist die schwarze Box NOCH DA?")
            print("Oder wieder das alte Bild?")

            if i < len(tests):
                input("\nENTER für nächsten Test...")

        print("\n" + "="*60)
        print("WELCHER TEST HAT DIE BOX BEHALTEN?")
        print("="*60)
        print("Wenn KEINER funktioniert:")
        print("  → Das Display hat evtl. einen Defekt")
        print("  → Oder es braucht einen speziellen Befehl")
        print("\nWenn EINER funktioniert:")
        print("  → NOTIERE DIR DIE NUMMER!")
        print("  → Das ist die Lösung!")
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
