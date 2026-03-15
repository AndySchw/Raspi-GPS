#!/usr/bin/env python3
"""
TEST MIT EXPLIZITEM CLEAR VOR JEDEM UPDATE

Problem: Alle Tests zeigen das gleiche Bild!
Vermutung: Display-RAM wird nicht gelöscht zwischen Tests

Lösung: Explizit das komplette RAM löschen (weiß) vor jedem neuen Muster
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TEST MIT EXPLIZITEM CLEAR")
print("="*60)

class ClearTester:
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

        self.cmd(0x12)  # SW Reset
        time.sleep(0.5)

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x24])

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x7F, 0x00])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temp
        self.data(0x80)

        # Reset RAM Pointer auf Anfang!
        self.cmd(0x4E)  # X Counter
        self.data(0x00)

        self.cmd(0x4F)  # Y Counter
        self.data([0x00, 0x00])

        time.sleep(0.2)

    def clear_white(self):
        """Explizit alles auf WEIß setzen"""
        print("   >>> CLEAR: Alles auf WEISS <<<")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Reset Pointer
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Black Buffer: WEISS (0xFF)
        self.cmd(0x24)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Reset Pointer nochmal
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Red Buffer: TRANSPARENT (0xFF)
        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Update
        self.cmd(0x20)
        time.sleep(3)
        print("   >>> Display sollte jetzt KOMPLETT WEISS sein! <<<")

    def clear_black(self):
        """Explizit alles auf SCHWARZ setzen"""
        print("   >>> CLEAR: Alles auf SCHWARZ <<<")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Reset Pointer
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Black Buffer: SCHWARZ (0x00)
        self.cmd(0x24)
        for _ in range(bytes_total):
            self.data(0x00)

        # Reset Pointer
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Red Buffer: TRANSPARENT (0xFF)
        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Update
        self.cmd(0x20)
        time.sleep(3)
        print("   >>> Display sollte jetzt KOMPLETT SCHWARZ sein! <<<")

    def clear_red(self):
        """Explizit alles auf ROT setzen"""
        print("   >>> CLEAR: Alles auf ROT <<<")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Reset Pointer
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Black Buffer: WEISS (0xFF)
        self.cmd(0x24)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Reset Pointer
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Red Buffer: ROT (0x00)
        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0x00)

        # Update
        self.cmd(0x20)
        time.sleep(3)
        print("   >>> Display sollte jetzt KOMPLETT ROT sein! <<<")

    def draw_simple_box(self):
        """Zeichne EINE EINZIGE schwarze Box in der Mitte"""
        print("   >>> DRAW: Schwarze Box in der Mitte <<<")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # ERST KOMPLETT LÖSCHEN!
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Black Buffer: WEISS überall
        self.cmd(0x24)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Red Buffer: TRANSPARENT
        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Jetzt Update (alles weiß)
        self.cmd(0x20)
        time.sleep(3)
        print("   >>> Sollte jetzt WEISS sein <<<")

        input("   ENTER zum Zeichnen der Box...")

        # JETZT Box zeichnen
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        # Black Buffer: Box in der Mitte (Y=40-88, X=120-176)
        self.cmd(0x24)
        for y in range(128):
            for x_byte in range(37):
                x_pixel = x_byte * 8
                # Box: Y 40-88, X 120-176
                if 40 <= y < 88 and 15 <= x_byte < 22:
                    self.data(0x00)  # Schwarz
                else:
                    self.data(0xFF)  # Weiß

        # Red Buffer bleibt transparent
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0xFF)

        # Update
        self.cmd(0x20)
        time.sleep(3)
        print("   >>> Sollte jetzt schwarze Box in der MITTE zeigen! <<<")


if __name__ == "__main__":
    print("\n⚠️  Dieser Test macht EXPLIZITE Clear-Operationen")
    print("Wir testen ob das Display überhaupt neue Daten akzeptiert!\n")

    try:
        tester = ClearTester()

        print("\n" + "="*60)
        print("TEST 1: Komplett WEISS")
        print("="*60)
        tester.init()
        tester.clear_white()
        input("\n>>> Ist das Display WEISS? ENTER für weiter...")

        print("\n" + "="*60)
        print("TEST 2: Komplett SCHWARZ")
        print("="*60)
        tester.init()
        tester.clear_black()
        input("\n>>> Ist das Display SCHWARZ? ENTER für weiter...")

        print("\n" + "="*60)
        print("TEST 3: Komplett ROT")
        print("="*60)
        tester.init()
        tester.clear_red()
        input("\n>>> Ist das Display ROT? ENTER für weiter...")

        print("\n" + "="*60)
        print("TEST 4: Schwarze Box in der Mitte")
        print("="*60)
        tester.init()
        tester.draw_simple_box()

        print("\n" + "="*60)
        print("ERGEBNISSE:")
        print("="*60)
        print("Hast du gesehen:")
        print("  1. Komplett weißes Display?")
        print("  2. Komplett schwarzes Display?")
        print("  3. Komplett rotes Display?")
        print("  4. Schwarze Box in der Mitte?")
        print("\nWenn NEIN bei allen:")
        print("  → Display akzeptiert KEINE neuen Daten!")
        print("  → RAM-Write ist kaputt oder deaktiviert")
        print("\nWenn JA bei 1-3, aber NEIN bei 4:")
        print("  → Koordinaten/Adressierung ist falsch")
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
