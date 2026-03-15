#!/usr/bin/env python3
"""
FARB-KORREKTUR TEST

Problem erkannt:
- Schwarz wird als Weiß angezeigt
- Weiß wird als Rot angezeigt
- Rot wird als Weiß angezeigt

Lösung: Wir invertieren die Buffers!
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 128
EPD_HEIGHT = 296

print("="*60)
print("FARB-KORREKTUR TEST")
print("="*60)

class ColorFixedDisplay:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

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
        """Initialisierung"""
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)
        time.sleep(0.5)

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)

        self.cmd(0x44)
        self.data([0x00, 0x0F])

        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x18)
        self.data(0x80)

        self.cmd(0x4E)
        self.data(0x00)

        self.cmd(0x4F)
        self.data([0x00, 0x00])

        time.sleep(0.2)

    def display(self, black_data, red_data):
        """Double-Update mit FARB-INVERTIERUNG"""

        # INVERTIERE DIE DATEN!
        # Alte Logik:
        #   black_data: 0x00=schwarz, 0xFF=weiß
        #   red_data:   0x00=rot,     0xFF=transparent

        # Neue Logik (invertiert):
        #   black_data: 0xFF=schwarz, 0x00=weiß  ← INVERTIERT!
        #   red_data:   0xFF=rot,     0x00=transparent ← INVERTIERT!

        inverted_black = [byte ^ 0xFF for byte in black_data]  # XOR mit 0xFF invertiert
        inverted_red = [byte ^ 0xFF for byte in red_data]

        # Durchgang 1
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x24)
        for byte in inverted_black:
            self.data(byte)

        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for byte in inverted_red:
            self.data(byte)

        self.cmd(0x20)
        time.sleep(2)

        # Durchgang 2
        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x24)
        for byte in inverted_black:
            self.data(byte)

        self.cmd(0x4E)
        self.data(0x00)
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.cmd(0x26)
        for byte in inverted_red:
            self.data(byte)

        self.cmd(0x20)
        time.sleep(2)

    def clear(self):
        """Lösche Display (weiß)"""
        bytes_total = (self.width * self.height) // 8
        black_data = [0xFF] * bytes_total  # Weiß
        red_data = [0xFF] * bytes_total    # Transparent
        self.display(black_data, red_data)

    def test_thirds_correct(self):
        """Drittel: Oben ROT, Mitte SCHWARZ, Unten WEISS"""
        print("\n>>> Test: Drittel (mit Farb-Korrektur) <<<")

        black_data = []
        red_data = []
        bytes_per_line = self.width // 8

        for y in range(self.height):
            for x_byte in range(bytes_per_line):
                if y < self.height // 3:
                    # Oben: ROT
                    black_data.append(0xFF)  # Weiß im Black-Buffer
                    red_data.append(0x00)    # Rot im Red-Buffer
                elif y < 2 * self.height // 3:
                    # Mitte: SCHWARZ
                    black_data.append(0x00)  # Schwarz
                    red_data.append(0xFF)    # Transparent
                else:
                    # Unten: WEISS
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0xFF)    # Transparent

        self.display(black_data, red_data)

    def test_text_correct(self):
        """Text-Test mit Farb-Korrektur"""
        print("\n>>> Test: Text (mit Farb-Korrektur) <<<")

        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=5)

        # Text in SCHWARZ
        draw_black.text((10, 30), "GPS", font=font_large, fill=0)
        draw_black.text((10, 90), "TEST", font=font_small, fill=0)

        # Text in ROT
        draw_red.text((10, 150), "ANDY", font=font_large, fill=0)

        # Schwarzes Rechteck
        draw_black.rectangle((10, 220, 50, 260), fill=0)

        # Rotes Rechteck
        draw_red.rectangle((68, 220, 108, 260), fill=0)

        black_data = list(black_img.tobytes())
        red_data = list(red_img.tobytes())

        self.display(black_data, red_data)

    def test_simple_boxes(self):
        """Einfacher Test: 3 Boxen in verschiedenen Farben"""
        print("\n>>> Test: 3 Boxen (Schwarz, Weiß, Rot) <<<")

        black_data = []
        red_data = []
        bytes_per_line = self.width // 8

        for y in range(self.height):
            for x_byte in range(bytes_per_line):
                x_pixel = x_byte * 8

                # Box 1 (oben, Y=20-80): SCHWARZ
                if 20 <= y < 80 and 20 <= x_pixel < 108:
                    black_data.append(0x00)  # Schwarz
                    red_data.append(0xFF)    # Transparent

                # Box 2 (mitte, Y=110-170): ROT
                elif 110 <= y < 170 and 20 <= x_pixel < 108:
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0x00)    # Rot

                # Box 3 (unten, Y=200-260): WEISS
                elif 200 <= y < 260 and 20 <= x_pixel < 108:
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0xFF)    # Transparent

                else:
                    # Hintergrund: WEISS
                    black_data.append(0xFF)
                    red_data.append(0xFF)

        self.display(black_data, red_data)


if __name__ == "__main__":
    print("\n⚠️  FARB-KORREKTUR TEST")
    print("Dieser Test invertiert die Farb-Buffer!\n")

    try:
        epd = ColorFixedDisplay()

        # Test 1: Clear
        print("\n" + "="*60)
        print("TEST 1: Clear (sollte WEISS sein)")
        print("="*60)
        epd.init()
        epd.clear()
        print(">>> Ist das Display WEISS (nicht rot)? <<<")
        input("ENTER für Test 2...")

        # Test 2: 3 Boxen
        print("\n" + "="*60)
        print("TEST 2: 3 Boxen")
        print("="*60)
        print("Erwarte von oben nach unten:")
        print("  - SCHWARZE Box")
        print("  - ROTE Box")
        print("  - WEISSE Box (auf weißem Hintergrund)")
        epd.init()
        epd.test_simple_boxes()
        print(">>> Sind die Farben RICHTIG? <<<")
        input("ENTER für Test 3...")

        # Test 3: Drittel
        print("\n" + "="*60)
        print("TEST 3: Drittel")
        print("="*60)
        print("Erwarte: Oben ROT, Mitte SCHWARZ, Unten WEISS")
        epd.init()
        epd.test_thirds_correct()
        print(">>> Sind die Farben RICHTIG? <<<")
        input("ENTER für Test 4...")

        # Test 4: Text
        print("\n" + "="*60)
        print("TEST 4: Text")
        print("="*60)
        print("Erwarte:")
        print("  - Schwarzer Rahmen")
        print("  - 'GPS TEST' in SCHWARZ")
        print("  - 'ANDY' in ROT")
        print("  - Schwarze + Rote Rechtecke")
        epd.init()
        epd.test_text_correct()
        print(">>> Sind die Farben RICHTIG? <<<")

        print("\n" + "="*60)
        print("ERGEBNIS:")
        print("="*60)
        print("Wenn die Farben jetzt RICHTIG sind:")
        print("  ✅ Farb-Invertierung funktioniert!")
        print("\nNächster Schritt:")
        print("  → 90° Rotation implementieren")
        print("  → Finalen Treiber schreiben")
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
