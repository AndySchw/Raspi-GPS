#!/usr/bin/env python3
"""
Display Test - BEIDE Buffer richtig nutzen
Problem: Nur Rot-Buffer wird angezeigt
Lösung: Schwarz-Buffer UND Rot-Buffer korrekt befüllen
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
print("DISPLAY TEST - BEIDE BUFFER")
print("="*60)

class BothBuffersEPD:
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

        # Schwarz-Buffer: 0xFF = weiß
        self.cmd(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.data(0xFF)

        # Rot-Buffer: 0xFF = weiß (KEIN Rot!)
        self.cmd(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Sollte KOMPLETT WEISS sein!")

    def show_test_image(self):
        print("\n3. Erstelle Testbild...")

        # Bild 128x296
        black_img = Image.new('1', (self.width, self.height), 255)  # Weiß
        red_img = Image.new('1', (self.width, self.height), 255)    # Weiß

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # SCHWARZER Rahmen (im Schwarz-Buffer)
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=5)

        # SCHWARZE Box oben (im Schwarz-Buffer)
        draw_black.rectangle((20, 20, 108, 80), fill=0)

        # ROTE Box Mitte (im Rot-Buffer)
        draw_red.rectangle((20, 110, 108, 170), fill=0)

        # SCHWARZE Box unten links (im Schwarz-Buffer)
        draw_black.rectangle((20, 200, 60, 240), fill=0)

        # ROTE Box unten rechts (im Rot-Buffer)
        draw_red.rectangle((68, 200, 108, 240), fill=0)

        # SCHWARZER Text (im Schwarz-Buffer)
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except:
            font = ImageFont.load_default()

        draw_black.text((20, 255), "GPS", font=font, fill=0)

        print("   ✅ Bild erstellt")
        print(f"   Schwarz-Bild: {black_img.size}")
        print(f"   Rot-Bild: {red_img.size}")

        print("\n4. Sende Bilddaten...")
        self.reset()

        # Schwarz-Buffer
        # 0 = schwarz zeigen, 1 = weiß (durchsichtig)
        self.cmd(0x24)
        black_bytes = black_img.tobytes()
        print(f"   Schwarz: {len(black_bytes)} Bytes")
        for byte in black_bytes:
            self.data(byte)  # NICHT invertieren

        # Rot-Buffer
        # 0 = rot zeigen, 1 = weiß (durchsichtig)
        self.cmd(0x26)
        red_bytes = red_img.tobytes()
        print(f"   Rot: {len(red_bytes)} Bytes")
        for byte in red_bytes:
            self.data(byte)  # NICHT invertieren

        print("\n5. Display Update...")
        self.cmd(0x20)

        print("   Warte 10 Sekunden...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n   ✅ Fertig!")


try:
    print("\n⚠️  Beide Buffer werden korrekt befüllt!")
    print("    Schwarz-Buffer: 0=schwarz, 1=weiß")
    print("    Rot-Buffer: 0=rot, 1=weiß\n")

    epd = BothBuffersEPD()
    epd.clear_white()
    time.sleep(2)
    epd.show_test_image()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Weißer Hintergrund")
    print("  - Schwarzer Rahmen")
    print("  - Schwarze Box oben")
    print("  - ROTE Box Mitte")
    print("  - Schwarze Box unten links")
    print("  - ROTE Box unten rechts")
    print("  - Text 'GPS' unten in SCHWARZ")
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
