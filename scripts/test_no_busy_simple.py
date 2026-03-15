#!/usr/bin/env python3
"""
EINFACHER TEST OHNE BUSY-PIN
Verwendet nur RST und DC, ignoriert BUSY komplett
Nutzt feste Wartezeiten statt BUSY-Check
"""

import time
import spidev
import RPi.GPIO as GPIO

# Minimale Pins - BUSY wird NICHT verwendet!
RST_PIN = 24  # Oder 17 - wir testen beide
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("SIMPLE TEST OHNE BUSY-PIN")
print("="*60)
print(f"RST:  GPIO{RST_PIN}")
print(f"DC:   GPIO{DC_PIN}")
print("BUSY: IGNORIERT (feste Wartezeiten)")
print("="*60)

class SimpleTester:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000  # Schneller SPI
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
        print("\n1. Hardware Reset...")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.01)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.01)
        print("   ✅ Reset OK")

    def init(self):
        """Minimale Init-Sequenz"""
        print("\n2. Initialisierung...")

        self.reset()
        time.sleep(0.2)

        # Software Reset
        self.cmd(0x12)
        time.sleep(1.0)  # Warte 1 Sekunde (statt BUSY)
        print("   ✅ Software Reset OK")

        # Driver Output Control
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        # Data Entry Mode (X inc, Y inc)
        self.cmd(0x11)
        self.data(0x03)

        # Set RAM X Address
        self.cmd(0x44)
        self.data([0x00, 0x24])  # 0x00 bis 0x24 (37 bytes = 296 pixel)

        # Set RAM Y Address
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

        # Border Waveform
        self.cmd(0x3C)
        self.data(0x05)

        # Temperature Sensor
        self.cmd(0x18)
        self.data(0x80)

        # Set RAM X Counter
        self.cmd(0x4E)
        self.data(0x00)

        # Set RAM Y Counter
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        time.sleep(0.2)
        print("   ✅ Init OK")

    def clear_white(self):
        """Komplett weiß"""
        print("\n3. Clear WHITE...")
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Black Buffer: 0xFF = weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)
        print("   ✅ Black Buffer gesendet (white)")

        # Red Buffer: 0xFF = transparent (zeigt weiß)
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)
        print("   ✅ Red Buffer gesendet (transparent)")

        # Display Update
        self.cmd(0x20)
        print("\n4. Warte 15 Sekunden auf Display-Update...")

        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n   ✅ Display sollte WEISS sein!")

    def draw_pattern(self):
        """Zeichne einfaches Muster"""
        print("\n5. Zeichne Muster...")
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Black Buffer: Streifen-Muster
        self.cmd(0x24)
        for i in range(bytes_total):
            # Horizontale Streifen: alle 8 Bytes wechseln
            if (i // 37) % 16 < 8:
                self.data(0x00)  # Schwarz
            else:
                self.data(0xFF)  # Weiß
        print("   ✅ Black Buffer: Streifen")

        # Red Buffer: Transparent
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)  # Transparent
        print("   ✅ Red Buffer: Transparent")

        # Display Update
        self.cmd(0x20)
        print("\n6. Warte 15 Sekunden auf Display-Update...")

        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n   ✅ Display sollte STREIFEN zeigen!")

    def draw_red_box(self):
        """Zeichne rote Box"""
        print("\n7. Zeichne ROTE Box...")
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Black Buffer: Alles weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)
        print("   ✅ Black Buffer: Weiß")

        # Red Buffer: Box in der Mitte
        self.cmd(0x26)
        for y in range(128):
            for x_byte in range(37):
                # Box: Y=40-88, X-Byte=10-27
                if 40 <= y < 88 and 10 <= x_byte < 27:
                    self.data(0x00)  # Rot
                else:
                    self.data(0xFF)  # Transparent (weiß)
        print("   ✅ Red Buffer: Rote Box")

        # Display Update
        self.cmd(0x20)
        print("\n8. Warte 15 Sekunden auf Display-Update...")

        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n   ✅ Display sollte ROTE BOX zeigen!")


if __name__ == "__main__":
    print("\n⚠️  Dieser Test ignoriert den BUSY-Pin komplett!")
    print("Wenn das funktioniert, dann ist BUSY einfach falsch/kaputt.\n")

    try:
        tester = SimpleTester()

        # Test 1: Init
        tester.init()

        # Test 2: Clear White
        tester.clear_white()

        input("\n>>> ENTER drücken für Test 2 (Streifen-Muster)...")

        # Test 3: Streifen
        tester.draw_pattern()

        input("\n>>> ENTER drücken für Test 3 (Rote Box)...")

        # Test 4: Rote Box
        tester.draw_red_box()

        print("\n" + "="*60)
        print("TESTS ABGESCHLOSSEN")
        print("="*60)
        print("\nWas hast du gesehen?")
        print("  1. Weißes Display?")
        print("  2. Streifen-Muster?")
        print("  3. Rote Box?")
        print("\nWenn JA -> BUSY-Pin ist das Problem!")
        print("Wenn NEIN -> RST/DC oder SPI-Verbindung falsch")
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
