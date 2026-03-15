#!/usr/bin/env python3
"""
TESTE BYTE-REIHENFOLGE UND BIT-ORIENTIERUNG

Das Bild zeigt: Daten kommen an, aber als "Pixel-Rauschen"!
Problem: Bytes werden in falscher Reihenfolge oder Bits sind vertauscht gesendet.

Wir testen:
1. Normale Byte-Reihenfolge
2. Bits innerhalb Byte invertiert (LSB <-> MSB)
3. Bytes zeilenweise rückwärts
4. Bytes komplett rückwärts
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TESTE BYTE-REIHENFOLGE UND BIT-ORIENTIERUNG")
print("="*60)

class ByteOrderTester:
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
        """Standard Init (wie gehabt)"""
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)  # Y inc, X inc

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

    def reverse_bits(self, byte):
        """Invertiere Bit-Reihenfolge innerhalb eines Bytes"""
        result = 0
        for i in range(8):
            if byte & (1 << i):
                result |= (1 << (7 - i))
        return result

    def create_simple_pattern(self):
        """
        Erstelle einfaches Muster ohne PIL:
        - Obere Hälfte: Vertikale Streifen (schwarz/weiß abwechselnd)
        - Untere Hälfte: Horizontale Streifen
        """
        pattern = []

        for y in range(128):
            for x_byte in range(37):
                if y < 64:
                    # Obere Hälfte: Vertikale Streifen
                    # Jedes zweite Byte schwarz/weiß
                    if x_byte % 2 == 0:
                        pattern.append(0xAA)  # 10101010 = vertikale Streifen
                    else:
                        pattern.append(0x55)  # 01010101 = vertikale Streifen invertiert
                else:
                    # Untere Hälfte: Horizontale Streifen
                    if (y // 4) % 2 == 0:
                        pattern.append(0x00)  # Schwarz
                    else:
                        pattern.append(0xFF)  # Weiß

        return pattern

    def send_pattern_normal(self, pattern):
        """Sende Muster normal (wie bisher)"""
        print("   Sende Muster: NORMAL (keine Transformation)")
        self.cmd(0x24)  # Black buffer
        for byte in pattern:
            self.data(byte)

        self.cmd(0x26)  # Red buffer (alles transparent)
        for _ in range(len(pattern)):
            self.data(0xFF)

    def send_pattern_bit_reversed(self, pattern):
        """Sende Muster mit INVERTIERTEN BITS"""
        print("   Sende Muster: BIT-REVERSED (LSB <-> MSB)")
        self.cmd(0x24)
        for byte in pattern:
            self.data(self.reverse_bits(byte))

        self.cmd(0x26)
        for _ in range(len(pattern)):
            self.data(0xFF)

    def send_pattern_line_reversed(self, pattern):
        """Sende jede Zeile RÜCKWÄRTS"""
        print("   Sende Muster: ZEILEN RÜCKWÄRTS")
        self.cmd(0x24)

        for y in range(128):
            # Hole die 37 Bytes dieser Zeile
            line_start = y * 37
            line_bytes = pattern[line_start:line_start + 37]
            # Sende rückwärts
            for byte in reversed(line_bytes):
                self.data(byte)

        self.cmd(0x26)
        for _ in range(len(pattern)):
            self.data(0xFF)

    def send_pattern_completely_reversed(self, pattern):
        """Sende ALLES RÜCKWÄRTS"""
        print("   Sende Muster: KOMPLETT RÜCKWÄRTS")
        self.cmd(0x24)
        for byte in reversed(pattern):
            self.data(byte)

        self.cmd(0x26)
        for _ in range(len(pattern)):
            self.data(0xFF)

    def send_pattern_bit_reversed_and_line_reversed(self, pattern):
        """Kombiniere: Bits invertiert UND Zeilen rückwärts"""
        print("   Sende Muster: BITS INVERTIERT + ZEILEN RÜCKWÄRTS")
        self.cmd(0x24)

        for y in range(128):
            line_start = y * 37
            line_bytes = pattern[line_start:line_start + 37]
            for byte in reversed(line_bytes):
                self.data(self.reverse_bits(byte))

        self.cmd(0x26)
        for _ in range(len(pattern)):
            self.data(0xFF)

    def update_display(self):
        """Update Display"""
        self.cmd(0x20)
        print("   Warte 3 Sekunden...")
        time.sleep(3)


if __name__ == "__main__":
    print("\n⚠️  Dieser Test zeigt 5 verschiedene Byte-Ordnungen")
    print("\nRICHTIGES BILD sollte zeigen:")
    print("  Oben:  Vertikale Streifen (schwarz/weiß)")
    print("  Unten: Horizontale Streifen (schwarz/weiß)")
    print("="*60)

    try:
        tester = ByteOrderTester()

        # Erstelle Muster einmal
        pattern = tester.create_simple_pattern()
        print(f"\nMuster erstellt: {len(pattern)} Bytes")

        tests = [
            ("NORMAL", tester.send_pattern_normal),
            ("BIT-REVERSED", tester.send_pattern_bit_reversed),
            ("ZEILEN RÜCKWÄRTS", tester.send_pattern_line_reversed),
            ("KOMPLETT RÜCKWÄRTS", tester.send_pattern_completely_reversed),
            ("BITS + ZEILEN RÜCKWÄRTS", tester.send_pattern_bit_reversed_and_line_reversed)
        ]

        for i, (name, send_func) in enumerate(tests, 1):
            print(f"\n\n{'='*60}")
            print(f"TEST {i}/5: {name}")
            print(f"{'='*60}")

            tester.init()
            send_func(pattern)
            tester.update_display()

            print("\n>>> SCHAU AUFS DISPLAY! <<<")
            print("Siehst du:")
            print("  - Oben: KLARE vertikale Streifen?")
            print("  - Unten: KLARE horizontale Streifen?")
            print("\nWenn JA: NOTIERE DIR DEN MODUS!")

            if i < len(tests):
                input("\nENTER für nächsten Test...")

        print("\n" + "="*60)
        print("WELCHER TEST HAT KLARE STREIFEN GEZEIGT?")
        print("="*60)
        print("1 = NORMAL")
        print("2 = BIT-REVERSED")
        print("3 = ZEILEN RÜCKWÄRTS")
        print("4 = KOMPLETT RÜCKWÄRTS")
        print("5 = BITS + ZEILEN RÜCKWÄRTS")
        print("\nSag mir die Nummer!")
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
