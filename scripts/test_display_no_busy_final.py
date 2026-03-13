#!/usr/bin/env python3
"""
Display-Test OHNE BUSY-Pin
Nutzt nur feste Wartezeiten
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# Pin-Definitionen (OHNE BUSY!)
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8

EPD_WIDTH = 128
EPD_HEIGHT = 296

class EPD_NoBusy:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)

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

    def reset(self):
        print("Hardware-Reset...")
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(RST_PIN, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.2)

    def init(self):
        print("\n1. Init Display (ohne BUSY-Check)...")
        self.reset()
        time.sleep(1)  # Feste Wartezeit

        print("2. Sende Init-Befehle...")
        self.send_command(0x12)  # SWRESET
        time.sleep(1)

        self.send_command(0x01)  # Driver output
        self.send_data([0x27, 0x01, 0x00])

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.send_command(0x44)  # Set RAM X
        self.send_data([0x00, 0x0F])

        self.send_command(0x45)  # Set RAM Y
        self.send_data([0x27, 0x01, 0x00, 0x00])

        self.send_command(0x3C)  # Border
        self.send_data(0x05)

        self.send_command(0x18)  # Temperature
        self.send_data(0x80)

        self.send_command(0x4E)  # Set X counter
        self.send_data(0x00)

        self.send_command(0x4F)  # Set Y counter
        self.send_data([0x27, 0x01])

        time.sleep(0.5)
        print("   ✅ Init OK")

    def clear_white(self):
        print("\n3. Lösche Display (weiß)...")

        # Schwarz-Buffer: 0xFF = weiß
        self.send_command(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0xFF)

        # Rot-Buffer: 0x00 = kein Rot
        self.send_command(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.send_data(0x00)

        print("4. Update Display...")
        self.send_command(0x20)

        print("5. Warte 15 Sekunden auf Display-Update...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n   ✅ Display sollte jetzt WEISS sein!")

    def show_test(self):
        print("\n6. Erstelle Testbild...")

        # Bilder erstellen
        black_img = Image.new('1', (self.width, self.height), 255)  # Weiß
        red_img = Image.new('1', (self.width, self.height), 255)    # Weiß

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # Großes schwarzes Rechteck oben
        draw_black.rectangle((10, 10, 118, 80), fill=0, outline=0)

        # Großes rotes Rechteck Mitte
        draw_red.rectangle((10, 100, 118, 170), fill=0, outline=0)

        # Schwarzes Rechteck unten
        draw_black.rectangle((10, 200, 50, 240), fill=0, outline=0)

        # Rotes Rechteck unten
        draw_red.rectangle((70, 200, 110, 240), fill=0, outline=0)

        print("   ✅ Bild erstellt")

        print("\n7. Sende Bilddaten...")

        # Schwarz-Buffer
        self.send_command(0x24)
        black_bytes = black_img.tobytes()
        for byte in black_bytes:
            self.send_data(byte)

        # Rot-Buffer
        self.send_command(0x26)
        red_bytes = red_img.tobytes()
        for byte in red_bytes:
            self.send_data(byte)

        print("8. Update Display...")
        self.send_command(0x20)

        print("9. Warte 15 Sekunden...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n   ✅ Display sollte jetzt Rechtecke zeigen!")

    def sleep(self):
        print("\n10. Sleep-Modus...")
        self.send_command(0x10)
        self.send_data(0x01)
        time.sleep(0.1)


print("="*60)
print("DISPLAY-TEST OHNE BUSY (Nur feste Wartezeiten)")
print("="*60)

try:
    # BUSY-Pin abziehen zur Sicherheit!
    print("\n⚠️  WICHTIG: BUSY-Pin (Lila Kabel) sollte ABGEZOGEN sein!")
    input("Drücke ENTER wenn bereit...")

    epd = EPD_NoBusy()
    epd.init()
    epd.clear_white()
    time.sleep(2)
    epd.show_test()
    epd.sleep()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN!")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Schwarzes Rechteck oben")
    print("  - ROTES Rechteck Mitte")
    print("  - Schwarzes + Rotes Rechteck unten")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
