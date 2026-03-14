#!/usr/bin/env python3
"""
Display Test mit KORRIGIERTEN FARBEN
Problem: Schwarz wird Weiß, Weiß wird Rot
Lösung: Bytes invertieren!
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
print("DISPLAY TEST MIT KORREKTEN FARBEN")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
print("Fix: Bytes werden invertiert!")
print("="*60)

class CorrectEPD:
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

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

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

    def reset(self):
        print("\n1. Hardware Reset...")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def clear_white(self):
        print("\n2. Lösche Display (weiß)...")
        self.reset()

        # INVERTIERT: 0x00 = weiß (war vorher 0xFF)
        self.cmd(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.data(0x00)

        # Rot-Buffer: 0x00 = kein Rot (bleibt gleich)
        self.cmd(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.data(0x00)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte WEISS sein!")

    def show_correct_image(self):
        print("\n3. Erstelle Testbild...")

        # Erstelle Bild 128x296
        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=5)

        # Schwarze Box oben
        draw_black.rectangle((20, 20, 108, 80), fill=0)

        # Rote Box Mitte
        draw_red.rectangle((20, 110, 108, 170), fill=0)

        # Schwarze Box unten links
        draw_black.rectangle((20, 200, 60, 240), fill=0)

        # Rote Box unten rechts
        draw_red.rectangle((68, 200, 108, 240), fill=0)

        # Text
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except:
            font = ImageFont.load_default()

        draw_black.text((20, 255), "GPS", font=font, fill=0)

        print("   ✅ Bild erstellt")

        print("\n4. Sende Bilddaten (INVERTIERT)...")
        self.reset()

        # Schwarz-Buffer - BYTES INVERTIEREN!
        self.cmd(0x24)
        black_bytes = black_img.tobytes()
        for byte in black_bytes:
            inverted = ~byte & 0xFF  # Invertiere Byte
            self.data(inverted)

        # Rot-Buffer - NICHT invertieren!
        self.cmd(0x26)
        red_bytes = red_img.tobytes()
        for byte in red_bytes:
            self.data(byte)  # NICHT invertiert

        print("\n5. Display Update...")
        self.cmd(0x20)

        print("   Warte 10 Sekunden...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n   ✅ Fertig!")


try:
    print("\n⚠️  Schwarz-Bytes werden INVERTIERT!\n")

    epd = CorrectEPD()
    epd.clear_white()
    time.sleep(2)
    epd.show_correct_image()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN")
    print("="*60)
    print("\nDu solltest jetzt sehen:")
    print("  - WEISSER Hintergrund")
    print("  - SCHWARZER Rahmen")
    print("  - SCHWARZE Boxen")
    print("  - ROTE Boxen")
    print("  - SCHWARZER Text 'GPS'")
    print("\nSind die Farben jetzt RICHTIG?")
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
