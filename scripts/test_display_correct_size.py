#!/usr/bin/env python3
"""
GDEW029Z10 Test mit KORREKTER Auflösung
WICHTIG: Display ist 296x128 (BREITE x HÖHE) - QUERFORMAT!
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Pin-Definitionen
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# KORRIGIERTE Display-Spezifikationen
EPD_WIDTH = 296   # Breite (war vorher falsch auf 128)
EPD_HEIGHT = 128  # Höhe (war vorher falsch auf 296)

print(f"""
{'='*60}
GDEW029Z10 Test mit KORREKTER Auflösung
{'='*60}
Display-Format: {EPD_WIDTH}x{EPD_HEIGHT} (Querformat!)
Bytes pro Bild: {int(EPD_WIDTH * EPD_HEIGHT / 8)}
{'='*60}
""")

class GDEW029Z10_Corrected:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000

    def send_command(self, command):
        GPIO.output(DC_PIN, GPIO.LOW)
        GPIO.output(CS_PIN, GPIO.LOW)
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, GPIO.HIGH)

    def send_data(self, data):
        GPIO.output(DC_PIN, GPIO.HIGH)
        GPIO.output(CS_PIN, GPIO.LOW)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, GPIO.HIGH)

    def wait_until_idle(self):
        """Warte bis BUSY-Pin HIGH ist"""
        print("  Warte auf Display (BUSY)...", end='', flush=True)
        timeout = 0
        while GPIO.input(BUSY_PIN) == GPIO.LOW:
            time.sleep(0.1)
            timeout += 1
            if timeout > 100:  # 10 Sekunden Timeout
                print(" TIMEOUT!")
                return
            if timeout % 10 == 0:
                print(".", end='', flush=True)
        print(" OK")

    def reset(self):
        print("  Hardware-Reset...")
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)

    def init(self):
        print("\n1. Initialisiere Display...")
        self.reset()
        self.wait_until_idle()

        print("2. Sende Init-Befehle...")
        self.send_command(0x12)  # SWRESET
        self.wait_until_idle()

        # Driver output control - WICHTIG für Auflösung!
        self.send_command(0x01)
        self.send_data([0x27, 0x01, 0x00])  # 296 Zeilen

        # Data entry mode
        self.send_command(0x11)
        self.send_data(0x03)  # X/Y increment

        # Set RAM X address (Breite / 8 = 296/8 = 37 = 0x25)
        self.send_command(0x44)
        self.send_data([0x00, 0x24])  # 0 bis 36 (0x24 = 36)

        # Set RAM Y address (Höhe = 128 = 0x7F)
        self.send_command(0x45)
        self.send_data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

        # Border waveform
        self.send_command(0x3C)
        self.send_data(0x05)

        # Temperature sensor
        self.send_command(0x18)
        self.send_data(0x80)

        # Set RAM X counter
        self.send_command(0x4E)
        self.send_data(0x00)

        # Set RAM Y counter
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])

        self.wait_until_idle()
        print("  ✅ Init abgeschlossen")

    def clear_white(self):
        """Komplett weiß machen"""
        print("\n3. Lösche Display (weiß)...")

        bytes_needed = int(self.width * self.height / 8)
        print(f"  Sende {bytes_needed} Bytes für {self.width}x{self.height} Pixel")

        # Schwarz-Buffer: 0xFF = weiß
        self.send_command(0x24)
        for i in range(bytes_needed):
            self.send_data(0xFF)

        # Rot-Buffer: 0x00 = kein Rot
        self.send_command(0x26)
        for i in range(bytes_needed):
            self.send_data(0x00)

        print("4. Update Display...")
        self.send_command(0x20)
        self.wait_until_idle()
        print("  ✅ Sollte jetzt WEISS sein")

    def show_test_pattern(self):
        """Zeige einfaches Testmuster"""
        print("\n5. Erstelle Testbild...")

        # Bilder mit KORREKTER Größe: 296x128 (Querformat!)
        black_img = Image.new('1', (self.width, self.height), 255)  # Weiß
        red_img = Image.new('1', (self.width, self.height), 255)    # Weiß

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Schwarzer Rahmen
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=3)

        # Schwarze Linie links (vertikal)
        draw_black.line((20, 10, 20, 118), fill=0, width=5)

        # Rote Linie rechts (vertikal)
        draw_red.line((275, 10, 275, 118), fill=0, width=5)

        # Schwarzes Rechteck oben links
        draw_black.rectangle((40, 20, 140, 60), fill=0)

        # Rotes Rechteck oben rechts
        draw_red.rectangle((160, 20, 260, 60), fill=0)

        # Text
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except:
            font = ImageFont.load_default()

        draw_black.text((50, 75), "GPS OK", font=font, fill=0)

        print(f"  Bild erstellt: {black_img.size}")

        print("\n6. Sende Bilddaten...")

        # Schwarz-Buffer
        self.send_command(0x24)
        black_bytes = black_img.tobytes()
        print(f"  Schwarz: {len(black_bytes)} Bytes")
        for byte in black_bytes:
            self.send_data(byte)

        # Rot-Buffer
        self.send_command(0x26)
        red_bytes = red_img.tobytes()
        print(f"  Rot: {len(red_bytes)} Bytes")
        for byte in red_bytes:
            self.send_data(byte)

        print("7. Update Display...")
        self.send_command(0x20)
        self.wait_until_idle()
        print("  ✅ Display sollte Testmuster zeigen!")

    def sleep(self):
        print("\n8. Sleep-Modus...")
        self.send_command(0x10)
        self.send_data(0x01)
        time.sleep(0.1)


try:
    epd = GDEW029Z10_Corrected()
    epd.init()
    epd.clear_white()
    time.sleep(2)
    epd.show_test_pattern()
    epd.sleep()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN!")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Schwarzer Rahmen")
    print("  - Schwarze Linie links, ROTE Linie rechts")
    print("  - Schwarzes Rechteck oben links")
    print("  - ROTES Rechteck oben rechts")
    print("  - Text 'GPS OK' in schwarz")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
