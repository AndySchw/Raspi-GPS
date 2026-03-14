#!/usr/bin/env python3
"""
Display Test mit ROTATION
PIL-Bilder müssen gedreht werden!
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
print("DISPLAY TEST MIT ROTATION")
print("="*60)

class RotatedEPD:
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
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def clear_white(self):
        print("\n1. Lösche Display (weiß)...")
        self.reset()

        self.cmd(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.data(0xFF)

        self.cmd(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Weiß!")

    def show_test_rotated(self):
        print("\n2. Erstelle Testbild...")

        # Erstelle Bild
        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Dicker schwarzer Rahmen
        draw_black.rectangle((5, 5, self.width-6, self.height-6), outline=0, width=8)

        # Große schwarze Box OBEN
        draw_black.rectangle((20, 30, 108, 100), fill=0)

        # Große ROTE Box MITTE
        draw_red.rectangle((20, 120, 108, 190), fill=0)

        # Text UNTEN
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
        except:
            font = ImageFont.load_default()

        draw_black.text((15, 230), "GPS", font=font, fill=0)

        print("   ✅ Bild erstellt (128x296)")

        # TESTE ALLE 4 ROTATIONEN!
        rotations = [
            (0, "0° (Normal)"),
            (90, "90° (Rechts gedreht)"),
            (180, "180° (Auf dem Kopf)"),
            (270, "270° (Links gedreht)")
        ]

        for angle, label in rotations:
            print(f"\n3. TEST: {label}")
            print("="*60)

            # Rotiere Bilder
            if angle > 0:
                black_rotated = black_img.rotate(angle, expand=True)
                red_rotated = red_img.rotate(angle, expand=True)

                # Auf korrekte Größe bringen
                if angle in [90, 270]:
                    # Bei 90/270° tauschen sich Width/Height
                    black_rotated = black_rotated.resize((self.width, self.height))
                    red_rotated = red_rotated.resize((self.width, self.height))
            else:
                black_rotated = black_img
                red_rotated = red_img

            print(f"   Rotiert: {black_rotated.size}")

            # Sende an Display
            self.reset()

            self.cmd(0x24)
            black_bytes = black_rotated.tobytes()
            for byte in black_bytes:
                self.data(byte)

            self.cmd(0x26)
            red_bytes = red_rotated.tobytes()
            for byte in red_bytes:
                self.data(byte)

            self.cmd(0x20)

            print("   Warte 8 Sekunden...")
            time.sleep(8)

            print(f"\n   >>> SCHAU AUFS DISPLAY <<<")
            print(f"   Rotation: {label}")
            print("   Siehst du:")
            print("     - Schwarzen RAHMEN?")
            print("     - Schwarze Box OBEN?")
            print("     - ROTE Box MITTE?")
            print("     - Text 'GPS' UNTEN?")

            response = input("\n   Ist das Bild RICHTIG? (j/n): ")
            if response.lower() == 'j':
                print(f"\n   ✅ {label} ist KORREKT!")
                break

        print("\n" + "="*60)
        print("TEST ABGESCHLOSSEN")
        print("="*60)


try:
    print("\n⚠️  Testet ALLE Rotationen (0°, 90°, 180°, 270°)!\n")

    epd = RotatedEPD()
    epd.clear_white()
    time.sleep(2)
    epd.show_test_rotated()

    GPIO.cleanup()

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
