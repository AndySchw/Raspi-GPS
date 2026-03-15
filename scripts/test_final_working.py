#!/usr/bin/env python3
"""
FINALER WORKING TEST

Wir haben herausgefunden:
- ZWEI Updates (0x20) nacheinander sind nötig!
- Daten kommen an, aber durcheinander

Jetzt testen wir verschiedene Auflösungen/Orientierungen
MIT der Double-Update-Methode!
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

print("="*60)
print("FINALER WORKING TEST - DOUBLE UPDATE")
print("="*60)

class FinalTester:
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

    def init_296x128(self):
        """Init für 296x128 (Querformat)"""
        print("   Init: 296x128 (Querformat)")
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)  # Y inc, X inc

        self.cmd(0x44)
        self.data([0x00, 0x24])  # 0-36 (37 bytes = 296 pixel)

        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])  # 0-127

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

    def init_128x296(self):
        """Init für 128x296 (Hochformat)"""
        print("   Init: 128x296 (Hochformat)")
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)

        self.cmd(0x44)
        self.data([0x00, 0x0F])  # 0-15 (16 bytes = 128 pixel)

        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])  # 0-295

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

    def double_update(self, width, height, black_data, red_data):
        """
        DOUBLE UPDATE METHODE (wie Test 5)
        Schreibe -> Update -> Schreibe nochmal -> Update
        """
        print("   Double Update Methode...")

        # === ERSTER DURCHGANG ===
        print("      1. Durchgang: Schreibe Daten...")
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x24)
        for byte in black_data:
            self.data(byte)

        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for byte in red_data:
            self.data(byte)

        print("      1. Update...")
        self.cmd(0x20)
        time.sleep(3)

        # === ZWEITER DURCHGANG ===
        print("      2. Durchgang: Schreibe Daten nochmal...")
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x24)
        for byte in black_data:
            self.data(byte)

        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for byte in red_data:
            self.data(byte)

        print("      2. Update...")
        self.cmd(0x20)
        time.sleep(3)

    def create_test_pattern(self, width, height):
        """
        Erstelle EINFACHES Test-Muster:
        - Komplette linke Hälfte: SCHWARZ
        - Komplette rechte Hälfte: ROT
        """
        bytes_per_line = width // 8
        total_bytes = bytes_per_line * height

        black_data = []
        red_data = []

        for y in range(height):
            for x_byte in range(bytes_per_line):
                # Linke Hälfte: Schwarz
                # Rechte Hälfte: Weiß (damit Rot sichtbar wird)
                if x_byte < bytes_per_line // 2:
                    black_data.append(0x00)  # Schwarz
                    red_data.append(0xFF)    # Transparent
                else:
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0x00)    # Rot

        return black_data, red_data

    def create_stripes_pattern(self, width, height):
        """
        Vertikale Streifen:
        - Jedes 2. Byte schwarz/weiß
        """
        bytes_per_line = width // 8
        black_data = []
        red_data = []

        for y in range(height):
            for x_byte in range(bytes_per_line):
                if x_byte % 2 == 0:
                    black_data.append(0x00)  # Schwarz
                else:
                    black_data.append(0xFF)  # Weiß
                red_data.append(0xFF)  # Alles transparent

        return black_data, red_data

    def test_clear_white(self, width, height):
        """Komplett weiß"""
        print("   Test: Komplett WEISS")
        bytes_total = (width * height) // 8

        black_data = [0xFF] * bytes_total
        red_data = [0xFF] * bytes_total

        self.double_update(width, height, black_data, red_data)


if __name__ == "__main__":
    print("\n⚠️  DIESER TEST VERWENDET DIE DOUBLE-UPDATE-METHODE!")
    print("Wir testen verschiedene Muster mit 296x128 und 128x296\n")

    try:
        tester = FinalTester()

        # === TEST 1: 296x128 mit Weiß ===
        print("\n" + "="*60)
        print("TEST 1: 296x128 - Komplett WEISS")
        print("="*60)
        width, height = tester.init_296x128()
        tester.test_clear_white(width, height)
        print(">>> Ist das Display WEISS? <<<")
        input("ENTER für weiter...")

        # === TEST 2: 296x128 mit Links/Rechts ===
        print("\n" + "="*60)
        print("TEST 2: 296x128 - Links SCHWARZ, Rechts ROT")
        print("="*60)
        width, height = tester.init_296x128()
        black_data, red_data = tester.create_test_pattern(width, height)
        tester.double_update(width, height, black_data, red_data)
        print(">>> Siehst du: Links SCHWARZ, Rechts ROT? <<<")
        input("ENTER für weiter...")

        # === TEST 3: 296x128 mit Streifen ===
        print("\n" + "="*60)
        print("TEST 3: 296x128 - Vertikale Streifen")
        print("="*60)
        width, height = tester.init_296x128()
        black_data, red_data = tester.create_stripes_pattern(width, height)
        tester.double_update(width, height, black_data, red_data)
        print(">>> Siehst du vertikale STREIFEN? <<<")
        input("ENTER für weiter...")

        # === TEST 4: 128x296 mit Links/Rechts ===
        print("\n" + "="*60)
        print("TEST 4: 128x296 - Links SCHWARZ, Rechts ROT")
        print("="*60)
        width, height = tester.init_128x296()
        black_data, red_data = tester.create_test_pattern(width, height)
        tester.double_update(width, height, black_data, red_data)
        print(">>> Siehst du: Links SCHWARZ, Rechts ROT? <<<")

        print("\n" + "="*60)
        print("WELCHER TEST HAT RICHTIG ANGEZEIGT?")
        print("="*60)
        print("Sag mir die Nummer (1-4)!")
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
