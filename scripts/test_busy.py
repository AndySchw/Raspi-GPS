#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# =========================
# PINBELEGUNG
# =========================
RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
# CS = GPIO8 / CE0 wird von spidev automatisch gesteuert

# =========================
# DISPLAYDATEN
# =========================
EPD_WIDTH = 296
EPD_HEIGHT = 128

# =========================
# E-PAPER KLASSE
# =========================
class EPD29TriColor:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)              # bus 0, CE0
        self.spi.max_speed_hz = 200000   # langsam und stabil zum Testen
        self.spi.mode = 0

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    def send_command(self, command):
        self.digital_write(DC_PIN, 0)
        self.spi.xfer2([command])

    def send_data(self, data):
        self.digital_write(DC_PIN, 1)
        if isinstance(data, int):
            self.spi.xfer2([data])
        else:
            self.spi.xfer2(list(data))

    def reset(self):
        self.digital_write(RST_PIN, 0)
        self.delay_ms(200)
        self.digital_write(RST_PIN, 1)
        self.delay_ms(200)

    def wait_until_idle(self, timeout=10):
        start = time.time()
        # 0 = busy, 1 = idle
        while self.digital_read(BUSY_PIN) == 0:
            if time.time() - start > timeout:
                print("❌ Timeout: Display bleibt busy")
                return False
            self.delay_ms(50)
        return True

    def init(self):
        print("Initialisiere Display...")
        self.reset()

        if not self.wait_until_idle(5):
            return False

        self.send_command(0x12)  # SWRESET
        self.delay_ms(200)
        if not self.wait_until_idle(5):
            return False

        # Driver output control
        self.send_command(0x01)
        self.send_data([0x27, 0x01, 0x00])  # 296 lines

        # Data entry mode
        self.send_command(0x11)
        self.send_data(0x03)

        # RAM X address start/end: 296 px / 8 = 37 bytes -> 0x24 inclusive
        self.send_command(0x44)
        self.send_data([0x00, 0x24])

        # RAM Y address start/end: 0..127
        self.send_command(0x45)
        self.send_data([0x00, 0x00, 0x7F, 0x00])

        # Border waveform
        self.send_command(0x3C)
        self.send_data(0x05)

        # Temperature sensor
        self.send_command(0x18)
        self.send_data(0x80)

        # RAM X address counter
        self.send_command(0x4E)
        self.send_data(0x00)

        # RAM Y address counter
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])

        if not self.wait_until_idle(5):
            return False

        print("✅ Init OK")
        return True

    def turn_on_display(self):
        self.send_command(0x20)
        return self.wait_until_idle(10)

    def sleep(self):
        self.send_command(0x10)
        self.send_data(0x01)
        self.delay_ms(100)

    def clear_white(self):
        print("Lösche Display auf weiß...")
        if not self.init():
            return False

        bytes_per_line = (EPD_WIDTH + 7) // 8
        total_bytes = bytes_per_line * EPD_HEIGHT

        # Schwarz-Buffer: 0xFF = weiß
        self.send_command(0x24)
        for _ in range(total_bytes):
            self.send_data(0xFF)

        # Rot-Buffer: 0xFF = kein Rot
        self.send_command(0x26)
        for _ in range(total_bytes):
            self.send_data(0xFF)

        if not self.turn_on_display():
            return False

        print("✅ Display ist weiß")
        return True

    def display_buffers(self, black_buffer, red_buffer):
        if len(black_buffer) != len(red_buffer):
            raise ValueError("Black- und Red-Buffer müssen gleich groß sein")

        if not self.init():
            return False

        self.send_command(0x24)
        self.send_data(black_buffer)

        self.send_command(0x26)
        self.send_data(red_buffer)

        if not self.turn_on_display():
            return False

        return True

# =========================
# HILFSFUNKTIONEN
# =========================
def image_to_buffer(img):
    """
    Wandelt ein PIL 1-bit Bild in einen Buffer für das E-Paper um.
    Erwartet Bildgröße 296x128.
    Weiß = 1, Schwarz = 0
    """
    if img.mode != "1":
        img = img.convert("1")

    if img.size != (EPD_WIDTH, EPD_HEIGHT):
        raise ValueError(f"Bild muss {EPD_WIDTH}x{EPD_HEIGHT} sein")

    pixels = img.load()
    buffer = []

    bytes_per_line = (EPD_WIDTH + 7) // 8

    for y in range(EPD_HEIGHT):
        for x_byte in range(bytes_per_line):
            byte = 0xFF
            for bit in range(8):
                x = x_byte * 8 + bit
                if x < EPD_WIDTH:
                    if pixels[x, y] == 0:  # schwarz
                        byte &= ~(0x80 >> bit)
            buffer.append(byte)

    return buffer

def create_test_bars():
    bytes_per_line = (EPD_WIDTH + 7) // 8
    total_bytes = bytes_per_line * EPD_HEIGHT

    black = [0xFF] * total_bytes
    red = [0xFF] * total_bytes

    # Schwarzer Balken links (ca. 40 Pixel)
    black_bar_bytes = 40 // 8

    for y in range(EPD_HEIGHT):
        for xb in range(bytes_per_line):
            index = y * bytes_per_line + xb
            if xb < black_bar_bytes:
                black[index] = 0x00

    # Roter Balken rechts (ca. 40 Pixel)
    red_bar_bytes = 40 // 8

    for y in range(EPD_HEIGHT):
        for xb in range(bytes_per_line):
            index = y * bytes_per_line + xb
            if xb >= bytes_per_line - red_bar_bytes:
                red[index] = 0x00

    return black, red

def create_text_test():
    black_img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
    red_img = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)

    draw_black = ImageDraw.Draw(black_img)
    draw_red = ImageDraw.Draw(red_img)

    # Rahmen
    draw_black.rectangle((0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1), outline=0, width=2)

    # Schwarzer Balken oben
    draw_black.rectangle((10, 10, 120, 40), fill=0)

    # Roter Balken darunter
    draw_red.rectangle((10, 50, 120, 80), fill=0)

    try:
        font_big = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
        )
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18
        )
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw_black.text((140, 15), "GPS", font=font_big, fill=0)
    draw_black.text((140, 50), "Tracker", font=font_small, fill=0)
    draw_red.text((140, 80), "TEST", font=font_big, fill=0)

    black_buffer = image_to_buffer(black_img)
    red_buffer = image_to_buffer(red_img)

    return black_buffer, red_buffer

# =========================
# HAUPTPROGRAMM
# =========================
def main():
    print("=" * 60)
    print("2.9 E-PAPER TEST - RASPBERRY PI ZERO 2 W")
    print("=" * 60)
    print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
    print("Pins:")
    print(f"  RST  = GPIO{RST_PIN}")
    print(f"  DC   = GPIO{DC_PIN}")
    print(f"  BUSY = GPIO{BUSY_PIN}")
    print("  CS   = CE0 / GPIO8 (automatisch)")
    print("=" * 60)

    epd = EPD29TriColor()

    try:
        print("\n[1/3] Weißtest...")
        if not epd.clear_white():
            print("❌ Weißtest fehlgeschlagen")
            return

        time.sleep(2)

        print("\n[2/3] Balkentest...")
        black, red = create_test_bars()
        if not epd.display_buffers(black, red):
            print("❌ Balkentest fehlgeschlagen")
            return
        print("✅ Schwarzer Balken links / roter Balken rechts")

        time.sleep(2)

        print("\n[3/3] Texttest...")
        black, red = create_text_test()
        if not epd.display_buffers(black, red):
            print("❌ Texttest fehlgeschlagen")
            return
        print("✅ Texttest gesendet")

        print("\nFertig.")
        print("Du solltest jetzt ungefähr sehen:")
        print("- schwarzen Rahmen")
        print("- schwarzen Balken oben")
        print("- roten Balken darunter")
        print("- Text: GPS / Tracker / TEST")

        epd.sleep()

    except KeyboardInterrupt:
        print("\nAbgebrochen.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        epd.spi.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()