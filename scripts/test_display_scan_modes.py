#!/usr/bin/env python3
"""
Test verschiedene Scan-Modi für GDEW029Z10
Data Entry Mode bestimmt wie die Daten ins Display geschrieben werden
"""

import time
import spidev
import RPi.GPIO as GPIO

# Pin-Definitionen
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("SCAN-MODE TEST")
print("="*60)

class EPD_ScanTest:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

    def cmd(self, command):
        GPIO.output(DC_PIN, 0)
        GPIO.output(CS_PIN, 0)
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, 1)

    def data(self, data):
        GPIO.output(DC_PIN, 1)
        GPIO.output(CS_PIN, 0)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, 1)

    def reset(self):
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 0)
        time.sleep(0.02)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def init(self, data_entry_mode=0x03):
        """Init mit konfigurierbarem Data Entry Mode"""
        print(f"\nInit mit Data Entry Mode: 0x{data_entry_mode:02X}")
        self.reset()
        time.sleep(1)

        self.cmd(0x12)  # SWRESET
        time.sleep(1)

        self.cmd(0x01)  # Driver output
        self.data([0x27, 0x01, 0x00])

        # DATA ENTRY MODE - DAS IST WICHTIG!
        self.cmd(0x11)
        self.data(data_entry_mode)
        print(f"  Data Entry Mode gesetzt: 0x{data_entry_mode:02X}")

        self.cmd(0x44)  # Set RAM X
        self.data([0x00, 0x24])

        self.cmd(0x45)  # Set RAM Y
        self.data([0x00, 0x00, 0x7F, 0x00])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temperature
        self.data(0x80)

        self.cmd(0x4E)  # Set X counter
        self.data(0x00)

        self.cmd(0x4F)  # Set Y counter
        self.data([0x00, 0x00])

        time.sleep(0.5)

    def show_corner_pattern(self):
        """Zeige Muster in allen 4 Ecken"""
        print("  Sende Eck-Muster...")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Schwarz-Buffer: 4 schwarze Quadrate in den Ecken
        self.cmd(0x24)

        # Erstelle Pattern: Erste 100 Bytes schwarz (oben links)
        for i in range(100):
            self.data(0x00)  # Schwarz

        # Rest weiß
        for i in range(bytes_total - 100):
            self.data(0xFF)  # Weiß

        # Rot-Buffer: Rotes Quadrat
        self.cmd(0x26)

        # Erste 100 Bytes weiß
        for i in range(100):
            self.data(0x00)  # Kein Rot

        # Nächste 100 Bytes rot (sollte woanders sein)
        for i in range(100):
            self.data(0xFF)  # Rot

        # Rest weiß
        for i in range(bytes_total - 200):
            self.data(0x00)  # Kein Rot

        # Update
        self.cmd(0x20)
        time.sleep(15)

    def sleep(self):
        self.cmd(0x10)
        self.data(0x01)


try:
    epd = EPD_ScanTest()

    # Teste verschiedene Data Entry Modes
    modes = [
        (0x03, "X inc, Y inc (Normal)"),
        (0x00, "X dec, Y dec"),
        (0x01, "X dec, Y inc"),
        (0x02, "X inc, Y dec"),
        (0x07, "Y inc, X inc (gedreht)"),
        (0x06, "Y inc, X dec (gedreht)"),
    ]

    for mode_val, mode_desc in modes:
        print("\n" + "="*60)
        print(f"TEST: {mode_desc}")
        print("="*60)

        epd.init(data_entry_mode=mode_val)
        epd.show_corner_pattern()

        print(f"\n>>> SCHAU AUFS DISPLAY <<<")
        print(f"    Mode 0x{mode_val:02X}: {mode_desc}")
        print(f"    Du solltest ein SCHWARZES und ein ROTES Quadrat sehen")
        print(f"    Merke dir WO sie sind!")

        input("\n[ENTER] für nächsten Mode...")

    epd.sleep()

    print("\n" + "="*60)
    print("TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWelcher Mode hat die Quadrate OBEN LINKS gezeigt?")
    print("Das ist dann der richtige Mode!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
