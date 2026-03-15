#!/usr/bin/env python3
"""
🎉 VICTORY TEST 🎉

Wir haben es geschafft! Funktionierende Konfiguration:
- Auflösung: 128x296 (Hochformat)
- Double-Update-Methode (2x schreiben, 2x update)
- Display ist 90° gedreht montiert

Jetzt testen wir verschiedene klare Muster!
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
print("🎉 VICTORY TEST - DISPLAY FUNKTIONIERT! 🎉")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
print("Methode: Double-Update")
print("="*60)

class WorkingDisplay:
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
        """Initialisierung für 128x296"""
        print("\n>>> Init Display <<<")
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)  # SW Reset
        time.sleep(0.5)

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)  # Y inc, X inc

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x0F])  # 0-15 (16 bytes = 128 pixel)

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x27, 0x01])  # 0-295

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temp
        self.data(0x80)

        self.cmd(0x4E)  # X Counter
        self.data(0x00)

        self.cmd(0x4F)  # Y Counter
        self.data([0x00, 0x00])

        time.sleep(0.2)
        print("    ✅ Init OK")

    def display(self, black_data, red_data):
        """
        DOUBLE-UPDATE-METHODE
        Zeige Daten mit 2x schreiben + 2x update
        """
        print(">>> Display Update (Double-Update-Methode) <<<")

        # === DURCHGANG 1 ===
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

        self.cmd(0x20)
        time.sleep(2)

        # === DURCHGANG 2 ===
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

        self.cmd(0x20)
        time.sleep(2)
        print("    ✅ Update OK")

    def clear(self):
        """Lösche Display (weiß)"""
        print(">>> Clear Display <<<")
        bytes_total = (self.width * self.height) // 8
        black_data = [0xFF] * bytes_total
        red_data = [0xFF] * bytes_total
        self.display(black_data, red_data)

    def test_pattern_thirds(self):
        """Drittelmuster: Oben ROT, Mitte SCHWARZ, Unten WEISS"""
        print("\n>>> Test: Drittel-Muster <<<")

        black_data = []
        red_data = []

        bytes_per_line = self.width // 8

        for y in range(self.height):
            for x_byte in range(bytes_per_line):
                if y < self.height // 3:
                    # Oberes Drittel: ROT
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0x00)    # Rot
                elif y < 2 * self.height // 3:
                    # Mittleres Drittel: SCHWARZ
                    black_data.append(0x00)  # Schwarz
                    red_data.append(0xFF)    # Transparent
                else:
                    # Unteres Drittel: WEISS
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0xFF)    # Transparent

        self.display(black_data, red_data)

    def test_pattern_frame(self):
        """Schwarzer Rahmen mit rotem Rechteck in der Mitte"""
        print("\n>>> Test: Rahmen + Rechteck <<<")

        black_data = []
        red_data = []

        bytes_per_line = self.width // 8

        for y in range(self.height):
            for x_byte in range(bytes_per_line):
                x_pixel = x_byte * 8

                # Schwarzer Rahmen (10 pixel breit)
                is_frame = (y < 10 or y >= self.height - 10 or
                           x_pixel < 10 or x_pixel >= self.width - 10)

                # Rotes Rechteck in der Mitte
                is_red_box = (80 <= y < 216 and 30 <= x_pixel < 98)

                if is_frame:
                    black_data.append(0x00)  # Schwarz
                    red_data.append(0xFF)    # Transparent
                elif is_red_box:
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0x00)    # Rot
                else:
                    black_data.append(0xFF)  # Weiß
                    red_data.append(0xFF)    # Transparent

        self.display(black_data, red_data)

    def test_with_text(self):
        """Test mit Text (PIL)"""
        print("\n>>> Test: Text mit PIL <<<")

        # Erstelle PIL Images
        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Font laden
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=3)

        # Text in Schwarz
        draw_black.text((10, 20), "GPS", font=font_large, fill=0)
        draw_black.text((10, 70), "DEVICE", font=font_small, fill=0)

        # Text in Rot
        draw_red.text((10, 120), "ANDY", font=font_large, fill=0)

        # Schwarzes Rechteck unten
        draw_black.rectangle((10, 200, 60, 250), fill=0)

        # Rotes Rechteck unten
        draw_red.rectangle((68, 200, 118, 250), fill=0)

        # Konvertiere zu Bytes
        black_data = list(black_img.tobytes())
        red_data = list(red_img.tobytes())

        self.display(black_data, red_data)


if __name__ == "__main__":
    print("\n⚠️  FINALE TESTS MIT FUNKTIONIERENDER KONFIGURATION!\n")

    try:
        epd = WorkingDisplay()
        epd.init()

        # Test 1: Clear
        print("\n" + "="*60)
        print("TEST 1: Clear (Weiß)")
        print("="*60)
        epd.clear()
        print(">>> Ist das Display WEISS? <<<")
        input("ENTER für Test 2...")

        # Test 2: Drittel
        print("\n" + "="*60)
        print("TEST 2: Drittel-Muster")
        print("="*60)
        print("Erwarte: Oben ROT, Mitte SCHWARZ, Unten WEISS")
        epd.init()
        epd.test_pattern_thirds()
        print(">>> Siehst du 3 klare Bereiche? <<<")
        input("ENTER für Test 3...")

        # Test 3: Rahmen
        print("\n" + "="*60)
        print("TEST 3: Rahmen + Rechteck")
        print("="*60)
        print("Erwarte: Schwarzer Rahmen + rotes Rechteck in Mitte")
        epd.init()
        epd.test_pattern_frame()
        print(">>> Siehst du Rahmen + rotes Rechteck? <<<")
        input("ENTER für Test 4...")

        # Test 4: Text
        print("\n" + "="*60)
        print("TEST 4: Text mit PIL")
        print("="*60)
        print("Erwarte: 'GPS DEVICE' schwarz, 'ANDY' rot, 2 Rechtecke")
        epd.init()
        epd.test_with_text()
        print(">>> Siehst du Text + Rechtecke? <<<")

        print("\n" + "="*60)
        print("🎉 GLÜCKWUNSCH! 🎉")
        print("="*60)
        print("\nDas Display funktioniert jetzt!")
        print("\nFINALE KONFIGURATION:")
        print(f"  - Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
        print("  - Methode: Double-Update (2x schreiben + 2x update)")
        print("  - BUSY-Pin: Ignoriert (feste Wartezeiten)")
        print("  - Rotation: Display ist 90° gedreht")
        print("\nNächste Schritte:")
        print("  1. Finalen Treiber in src/display/ implementieren")
        print("  2. Rotation in Software korrigieren")
        print("  3. PIL-Integration optimieren")
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
