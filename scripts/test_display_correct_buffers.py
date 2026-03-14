#!/usr/bin/env python3
"""
Test: KORREKTE Buffer-Zuordnung
Die Blöcke sind jetzt vertikal (gut!), aber Farben sind falsch
Lösung: Buffer richtig befüllen
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

EPD_WIDTH = 128
EPD_HEIGHT = 296

print("="*60)
print("KORREKTE BUFFER-ZUORDNUNG")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT} (Hochformat!)")
print("="*60)

class CorrectBuffers:
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
        """Init mit korrekten Einstellungen"""
        print("\n1. Init Display...")
        self.reset()
        self.wait_busy()

        self.cmd(0x12)  # SWRESET
        time.sleep(0.3)
        self.wait_busy()

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)  # Y inc, X inc

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x0F])

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x27, 0x01])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temperature
        self.data(0x80)

        self.cmd(0x4E)  # X Counter
        self.data(0x00)

        self.cmd(0x4F)  # Y Counter
        self.data([0x00, 0x00])

        self.wait_busy()
        print("   ✅ Init OK")

    def clear_white(self):
        """Komplett weiß"""
        print("\n2. Lösche Display (weiß)...")
        self.init()

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Schwarz-Buffer: 0xFF = weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        # Rot-Buffer: 0xFF = kein Rot (weiß)
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte KOMPLETT WEISS sein!")

    def show_test_image(self):
        """Test mit PIL"""
        print("\n3. Erstelle Testbild mit PIL...")
        self.init()

        # Bilder 128x296 (Hochformat!)
        black_img = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
        red_img = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, EPD_WIDTH-1, EPD_HEIGHT-1), outline=0, width=5)

        # Schwarzes Rechteck OBEN
        draw_black.rectangle((20, 30, 108, 100), fill=0)

        # Rotes Rechteck MITTE
        draw_red.rectangle((20, 120, 108, 190), fill=0)

        # Schwarzer Text UNTEN
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
        except:
            font = ImageFont.load_default()

        draw_black.text((20, 230), "GPS", font=font, fill=0)

        print("   ✅ Bild erstellt: 128x296")

        print("\n4. Sende Bilddaten...")

        # Schwarz-Buffer
        self.cmd(0x24)
        black_bytes = black_img.tobytes()
        print(f"   Schwarz: {len(black_bytes)} Bytes")
        for byte in black_bytes:
            self.data(byte)

        # Rot-Buffer
        self.cmd(0x26)
        red_bytes = red_img.tobytes()
        print(f"   Rot: {len(red_bytes)} Bytes")
        for byte in red_bytes:
            self.data(byte)

        self.cmd(0x20)
        print("\n5. Update...")
        time.sleep(10)
        print("   ✅ Fertig!")


try:
    print("\n⚠️  Mit vollständiger Init-Sequenz!\n")

    epd = CorrectBuffers()
    epd.clear_white()
    time.sleep(2)
    epd.show_test_image()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Weißer Hintergrund")
    print("  - Schwarzer Rahmen")
    print("  - Schwarzes Rechteck oben")
    print("  - ROTES Rechteck Mitte")
    print("  - Schwarzer Text 'GPS' unten")
    print("\nWas siehst du?")
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
