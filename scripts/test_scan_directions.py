#!/usr/bin/env python3
"""
TESTE ALLE SCAN-RICHTUNGEN
Data Entry Mode hat 8 verschiedene Modi (0x00 - 0x07)

Das rote Rechteck oben rechts zeigt: Scan-Richtung ist FALSCH!
Wir testen ALLE Kombinationen.
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TESTE ALLE SCAN-RICHTUNGEN")
print("="*60)

class ScanTester:
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

    def init(self, data_entry_mode):
        """Init mit spezifischem Data Entry Mode"""
        self.reset()
        time.sleep(0.2)

        # Software Reset
        self.cmd(0x12)
        time.sleep(0.5)

        # Driver Output Control
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        # !!! DER WICHTIGE TEIL !!!
        # Data Entry Mode (bestimmt Scan-Richtung)
        self.cmd(0x11)
        self.data(data_entry_mode)

        # Set RAM X Address
        self.cmd(0x44)
        self.data([0x00, 0x24])  # 0x00 bis 0x24 (37 bytes)

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

    def draw_corner_boxes(self):
        """Zeichne 4 rote Boxen in allen Ecken + schwarzes Kreuz in Mitte"""
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Black Buffer: Schwarzes Kreuz in der Mitte
        self.cmd(0x24)
        for y in range(128):
            for x_byte in range(37):
                x_pixel = x_byte * 8

                # Horizontale Linie in der Mitte (Y=60-68)
                # Vertikale Linie in der Mitte (X=140-156)
                if 60 <= y < 68 or (140 <= x_pixel < 156):
                    self.data(0x00)  # Schwarz
                else:
                    self.data(0xFF)  # Weiß

        # Red Buffer: 4 Ecken
        self.cmd(0x26)
        for y in range(128):
            for x_byte in range(37):
                x_pixel = x_byte * 8

                # Oben Links (Y=0-20, X=0-40)
                # Oben Rechts (Y=0-20, X=256-296)
                # Unten Links (Y=108-128, X=0-40)
                # Unten Rechts (Y=108-128, X=256-296)

                is_top_left = (y < 20 and x_pixel < 40)
                is_top_right = (y < 20 and x_pixel >= 256)
                is_bottom_left = (y >= 108 and x_pixel < 40)
                is_bottom_right = (y >= 108 and x_pixel >= 256)

                if is_top_left or is_top_right or is_bottom_left or is_bottom_right:
                    self.data(0x00)  # Rot
                else:
                    self.data(0xFF)  # Transparent

        # Display Update
        self.cmd(0x20)
        time.sleep(3)  # Kurze Wartezeit


# Data Entry Mode Erklärung:
# Bit 0-1: X-Richtung und Y-Richtung
#   0x00 = Y dec, X dec
#   0x01 = Y dec, X inc
#   0x02 = Y inc, X dec
#   0x03 = Y inc, X inc ← STANDARD (war in deinem Test)
#   0x04 = X dec, Y dec
#   0x05 = X dec, Y inc
#   0x06 = X inc, Y dec
#   0x07 = X inc, Y inc

DATA_ENTRY_MODES = {
    0x00: "Y dec, X dec",
    0x01: "Y dec, X inc",
    0x02: "Y inc, X dec",
    0x03: "Y inc, X inc (STANDARD)",
    0x04: "X dec, Y dec",
    0x05: "X dec, Y inc",
    0x06: "X inc, Y dec",
    0x07: "X inc, Y inc"
}

if __name__ == "__main__":
    print("\n⚠️  Dieser Test zeigt dir 8 verschiedene Scan-Modi")
    print("Bei jedem Modus solltest du sehen:")
    print("  - 4 ROTE Boxen in den Ecken")
    print("  - 1 SCHWARZES Kreuz in der Mitte")
    print("\nWenn die Boxen an den RICHTIGEN Positionen sind:")
    print("  → Dann hast du den RICHTIGEN Data Entry Mode!")
    print("="*60)

    try:
        tester = ScanTester()

        for mode in range(8):
            print(f"\n\n{'='*60}")
            print(f"TEST {mode+1}/8: Data Entry Mode = 0x{mode:02X}")
            print(f"Beschreibung: {DATA_ENTRY_MODES[mode]}")
            print(f"{'='*60}")

            tester.init(mode)
            tester.draw_corner_boxes()

            print("\n>>> SCHAU AUFS DISPLAY! <<<")
            print("Siehst du:")
            print("  - 4 rote Boxen in den Ecken?")
            print("  - 1 schwarzes Kreuz in der Mitte?")
            print("\nWenn JA: NOTIERE DIR DEN MODUS 0x{:02X}!".format(mode))

            if mode < 7:
                input("\nENTER für nächsten Modus...")
            else:
                print("\nLetzter Modus - fertig!")

        print("\n" + "="*60)
        print("ALLE MODI GETESTET")
        print("="*60)
        print("\nWelcher Modus hat KORREKT angezeigt?")
        print("Notiere die Nummer und sag mir Bescheid!")
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
