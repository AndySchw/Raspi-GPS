#!/usr/bin/env python3
"""
TESTE VERSCHIEDENE AUFLÖSUNGEN UND ORIENTIERUNGEN

Bei Modus 3 waren die Boxen falsch positioniert.
Mögliche Ursachen:
1. Auflösung ist 128x296 (Hochformat) statt 296x128 (Querformat)
2. RAM-Adressierung ist falsch
3. Display ist gedreht montiert
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

print("="*60)
print("TESTE VERSCHIEDENE AUFLÖSUNGEN")
print("="*60)

class ResolutionTester:
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

    def init_variant1(self):
        """
        VARIANTE 1: 296x128 (Querformat)
        Das haben wir bisher benutzt
        """
        print("\n=== VARIANTE 1: 296x128 (QUERFORMAT) ===")

        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)  # SW Reset
        time.sleep(0.5)

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)  # Y inc, X inc

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x24])  # 0 bis 0x24 (37 bytes = 296 pixel)

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x18)
        self.data(0x80)

        self.cmd(0x4E)
        self.data(0x00)

        self.cmd(0x4F)
        self.data([0x00, 0x00])

        time.sleep(0.2)
        return 296, 128

    def init_variant2(self):
        """
        VARIANTE 2: 128x296 (Hochformat)
        Vielleicht ist das Display tatsächlich so orientiert?
        """
        print("\n=== VARIANTE 2: 128x296 (HOCHFORMAT) ===")

        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)  # SW Reset
        time.sleep(0.5)

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen (bleibt gleich - Hardware!)

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)  # Y inc, X inc

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x0F])  # 0 bis 0x0F (16 bytes = 128 pixel)

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x27, 0x01])  # 0 bis 295

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x18)
        self.data(0x80)

        self.cmd(0x4E)
        self.data(0x00)

        self.cmd(0x4F)
        self.data([0x00, 0x00])

        time.sleep(0.2)
        return 128, 296

    def init_variant3(self):
        """
        VARIANTE 3: 296x128 aber mit anderen RAM-Startwerten
        """
        print("\n=== VARIANTE 3: 296x128 mit Start bei Ende ===")

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

        # Start am ENDE statt am Anfang
        self.cmd(0x4E)
        self.data(0x24)  # Start bei 0x24 (Ende)

        self.cmd(0x4F)
        self.data([0x7F, 0x00])  # Start bei 127 (Ende)

        time.sleep(0.2)
        return 296, 128

    def draw_test_pattern(self, width, height):
        """
        Zeichne eindeutiges Test-Muster:
        - Rote Box OBEN LINKS
        - Schwarze Box OBEN RECHTS
        - Schwarze Box UNTEN LINKS
        - Rote Box UNTEN RECHTS
        + Schwarzer Rahmen
        """
        bytes_total = int(width * height / 8)

        # Black Buffer: Rahmen + 2 schwarze Boxen
        self.cmd(0x24)

        for y in range(height):
            for x_byte in range(width // 8):
                x_pixel = x_byte * 8

                byte_val = 0xFF  # Default: weiß

                # Rahmen (2 pixel breit)
                if y < 2 or y >= height - 2 or x_pixel < 16 or x_pixel >= width - 16:
                    byte_val = 0x00  # Schwarz

                # Box OBEN RECHTS (Y=10-40, X=width-60 bis width-20)
                elif 10 <= y < 40 and width - 60 <= x_pixel < width - 20:
                    byte_val = 0x00  # Schwarz

                # Box UNTEN LINKS (Y=height-40 bis height-10, X=20-60)
                elif height - 40 <= y < height - 10 and 20 <= x_pixel < 60:
                    byte_val = 0x00  # Schwarz

                self.data(byte_val)

        # Red Buffer: 2 rote Boxen
        self.cmd(0x26)

        for y in range(height):
            for x_byte in range(width // 8):
                x_pixel = x_byte * 8

                byte_val = 0xFF  # Default: transparent

                # Box OBEN LINKS (Y=10-40, X=20-60)
                if 10 <= y < 40 and 20 <= x_pixel < 60:
                    byte_val = 0x00  # Rot

                # Box UNTEN RECHTS (Y=height-40 bis height-10, X=width-60 bis width-20)
                elif height - 40 <= y < height - 10 and width - 60 <= x_pixel < width - 20:
                    byte_val = 0x00  # Rot

                self.data(byte_val)

        # Update
        self.cmd(0x20)
        time.sleep(3)


if __name__ == "__main__":
    print("\n⚠️  Dieser Test zeigt 3 verschiedene Konfigurationen")
    print("\nRICHTIGES BILD sollte zeigen:")
    print("  ┌─────────────────┐")
    print("  │ ROT  │  SCHWARZ │  ← Oben")
    print("  │──────┼──────────│")
    print("  │SCHWARZ│   ROT   │  ← Unten")
    print("  └─────────────────┘")
    print("  + Schwarzer Rahmen rundherum")
    print("="*60)

    try:
        tester = ResolutionTester()

        # Test 1
        print("\n\nTEST 1/3")
        width, height = tester.init_variant1()
        tester.draw_test_pattern(width, height)
        print("\n>>> SCHAU AUFS DISPLAY <<<")
        print("Siehst du das richtige Muster?")
        input("ENTER für Test 2...")

        # Test 2
        print("\n\nTEST 2/3")
        width, height = tester.init_variant2()
        tester.draw_test_pattern(width, height)
        print("\n>>> SCHAU AUFS DISPLAY <<<")
        print("Siehst du das richtige Muster?")
        input("ENTER für Test 3...")

        # Test 3
        print("\n\nTEST 3/3")
        width, height = tester.init_variant3()
        tester.draw_test_pattern(width, height)
        print("\n>>> SCHAU AUFS DISPLAY <<<")
        print("Siehst du das richtige Muster?")

        print("\n" + "="*60)
        print("WELCHER TEST HAT RICHTIG ANGEZEIGT?")
        print("="*60)
        print("Test 1 = 296x128 Querformat (Standard)")
        print("Test 2 = 128x296 Hochformat")
        print("Test 3 = 296x128 mit anderem Startpunkt")
        print("\nSag mir die Nummer (1, 2 oder 3)!")
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
