#!/usr/bin/env python3
"""
ERFOLGREICHER DISPLAY-TREIBER!
Schwarz-Buffer: 0x24, 0x00=schwarz, 0xFF=weiß
Rot-Buffer: 0x26, 0x00=rot, 0xFF=transparent
Orientierung: 296x128 (Querformat!)
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# WICHTIG: Display ist 296x128 (QUERFORMAT!)
EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("🎉 ERFOLGREICHER DISPLAY-TREIBER!")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT} (Querformat)")
print("="*60)

class SuccessEPD:
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

    def clear(self):
        """Lösche Display - weiß"""
        print("\n2. Lösche Display...")
        self.reset()

        bytes_total = int(self.width * self.height / 8)

        # Schwarz-Buffer: 0xFF = weiß
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        # Rot-Buffer: 0xFF = kein Rot
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x20)
        print("   Warte 10 Sekunden...")
        time.sleep(10)
        print("   ✅ Display gelöscht!")

    def display_image(self, black_image, red_image):
        """Zeige Bild an"""
        print("\n3. Sende Bild...")
        self.reset()

        # Schwarz-Buffer
        self.cmd(0x24)
        black_bytes = black_image.tobytes()
        for byte in black_bytes:
            self.data(byte)

        # Rot-Buffer
        self.cmd(0x26)
        red_bytes = red_image.tobytes()
        for byte in red_bytes:
            self.data(byte)

        self.cmd(0x20)
        print("   Update Display...")
        time.sleep(10)
        print("   ✅ Fertig!")

    def show_gps_screen(self):
        """Zeige GPS-Demo-Screen"""
        print("\n4. Erstelle GPS-Demo...")

        # Bilder 296x128 (Querformat!)
        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # SCHWARZER Rahmen
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=3)

        # SCHWARZER Titel oben
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            font_data = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        except:
            font_title = ImageFont.load_default()
            font_data = ImageFont.load_default()

        draw_black.text((10, 10), "GPS TRACKER", font=font_title, fill=0)

        # ROTE Linie unter Titel
        draw_red.line((10, 45, self.width-10, 45), fill=0, width=2)

        # SCHWARZE Daten links
        draw_black.text((10, 55), "Lat: 48.1234", font=font_data, fill=0)
        draw_black.text((10, 80), "Lon: 11.5678", font=font_data, fill=0)

        # ROTE Status-Box rechts
        draw_red.rectangle((200, 55, 280, 110), outline=0, width=2)
        draw_red.text((210, 70), "GPS OK", font=font_data, fill=0)

        print("   ✅ Bild erstellt: 296x128")

        self.display_image(black_img, red_img)


try:
    print("\n🎉 ENDLICH! Display funktioniert!\n")

    epd = SuccessEPD()
    epd.clear()
    time.sleep(2)
    epd.show_gps_screen()

    print("\n" + "="*60)
    print("✅ ERFOLG!")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Schwarzer Rahmen")
    print("  - Schwarzer Text 'GPS TRACKER' oben")
    print("  - ROTE Linie unter Titel")
    print("  - Schwarze GPS-Daten links")
    print("  - ROTE Box rechts mit 'GPS OK'")
    print("\nFUNKTIONIERT ES? 🎉")
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
