#!/usr/bin/env python3
"""
GDEW029Z10 Test OHNE BUSY-Pin
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

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("DISPLAY TEST OHNE BUSY-PIN")
print("="*60)
print(f"Display: {EPD_WIDTH}x{EPD_HEIGHT} (Querformat)")
print(f"Bytes: {int(EPD_WIDTH * EPD_HEIGHT / 8)}")
print("="*60)

class EPD_NoBusy:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        # BUSY_PIN wird NICHT mehr verwendet!

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000  # 2 MHz
        self.spi.mode = 0

        print(f"SPI Speed: {self.spi.max_speed_hz} Hz")

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
        print("\n1. Hardware-Reset...")
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 0)
        time.sleep(0.02)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def init(self):
        print("2. Init Display...")
        self.reset()
        time.sleep(1)  # Feste Wartezeit statt BUSY

        self.cmd(0x12)  # SWRESET
        time.sleep(1)   # Feste Wartezeit

        self.cmd(0x01)  # Driver output
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)  # Data entry mode
        self.data(0x03)

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
        print("   ✅ Init OK")

    def clear_white(self):
        print("\n3. Lösche Display (weiß)...")

        # Schwarz-Buffer
        self.cmd(0x24)
        for i in range(int(self.width * self.height / 8)):
            self.data(0xFF)

        # Rot-Buffer
        self.cmd(0x26)
        for i in range(int(self.width * self.height / 8)):
            self.data(0x00)

        print("4. Update Display...")
        self.cmd(0x20)

        print("5. Warte 15 Sekunden...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n   ✅ Sollte WEISS sein!")

    def show_test(self):
        print("\n6. Erstelle Testbild...")

        # Bilder mit korrekter Größe
        black_img = Image.new('1', (self.width, self.height), 255)
        red_img = Image.new('1', (self.width, self.height), 255)

        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)

        # GROSSER schwarzer Rahmen (dick!)
        draw_black.rectangle((0, 0, self.width-1, self.height-1), outline=0, width=5)

        # GROSSE schwarze Box links oben
        draw_black.rectangle((10, 10, 90, 50), fill=0)

        # GROSSE rote Box rechts oben
        draw_red.rectangle((200, 10, 280, 50), fill=0)

        # GROSSE schwarze Box links unten
        draw_black.rectangle((10, 70, 90, 110), fill=0)

        # GROSSE rote Box rechts unten
        draw_red.rectangle((200, 70, 280, 110), fill=0)

        # Großer Text in der Mitte
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except:
            font = ImageFont.load_default()

        draw_black.text((100, 45), "GPS", font=font, fill=0)

        print("   ✅ Bild erstellt")

        print("7. Sende Bilddaten...")

        # Schwarz-Buffer
        self.cmd(0x24)
        black_bytes = black_img.tobytes()
        for byte in black_bytes:
            self.data(byte)

        # Rot-Buffer
        self.cmd(0x26)
        red_bytes = red_img.tobytes()
        for byte in red_bytes:
            self.data(byte)

        print("8. Update Display...")
        self.cmd(0x20)

        print("9. Warte 15 Sekunden...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)
        print("\n   ✅ Sollte Testbild zeigen!")

    def sleep(self):
        print("\n10. Sleep...")
        self.cmd(0x10)
        self.data(0x01)


try:
    print("\n⚠️  BUSY-Pin wird IGNORIERT (funktioniert nicht)!")
    print("    Wir nutzen nur feste Wartezeiten.\n")

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
    print("  - Dicker schwarzer Rahmen")
    print("  - Schwarze Box links oben")
    print("  - ROTE Box rechts oben")
    print("  - Schwarze Box links unten")
    print("  - ROTE Box rechts unten")
    print("  - Text 'GPS' in der Mitte")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
