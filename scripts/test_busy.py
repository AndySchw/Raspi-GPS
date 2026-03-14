#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont

# =========================
# PINS
# =========================
RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
# CS = CE0 / GPIO8 via spidev

# =========================
# SICHTBARE AUSRICHTUNG
# =========================
DISPLAY_WIDTH = 296
DISPLAY_HEIGHT = 128

# =========================
# CONTROLLER-RAM
# =========================
RAM_WIDTH = 128
RAM_HEIGHT = 296

class EPD29:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 200000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        if isinstance(d, int):
            self.spi.xfer2([d])
        else:
            self.send_data_chunked(d)

    def send_data_chunked(self, data, chunk_size=1024):
        data_list = list(data)
        for i in range(0, len(data_list), chunk_size):
            self.spi.xfer2(data_list[i:i + chunk_size])

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def wait_idle(self, timeout=10):
        start = time.time()
        # 0 = busy, 1 = idle
        while GPIO.input(BUSY_PIN) == 0:
            if time.time() - start > timeout:
                print("❌ Timeout: BUSY bleibt 0")
                return False
            time.sleep(0.05)
        return True

    def init(self):
        print("Initialisiere Display...")
        self.reset()

        if not self.wait_idle(5):
            return False

        self.cmd(0x12)  # SWRESET
        time.sleep(0.2)
        if not self.wait_idle(5):
            return False

        # Controller-native: 296 Zeilen
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        # Data entry
        self.cmd(0x11)
        self.data(0x03)

        # RAM X: 128 Pixel / 8 = 16 Bytes => 0x0F
        self.cmd(0x44)
        self.data([0x00, 0x0F])

        # RAM Y: 296 Zeilen => 0x0127
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

        if not self.wait_idle(5):
            return False

        print("✅ Init OK")
        return True

    def refresh(self):
        self.cmd(0x20)
        return self.wait_idle(10)

    def sleep(self):
        self.cmd(0x10)
        self.data(0x01)
        time.sleep(0.1)

    def clear_white(self):
        if not self.init():
            return False

        total = (RAM_WIDTH // 8) * RAM_HEIGHT  # 16 * 296 = 4736

        self.cmd(0x24)
        for _ in range(total):
            self.data(0xFF)

        self.cmd(0x26)
        for _ in range(total):
            self.data(0xFF)

        return self.refresh()

    def display(self, black_buf, red_buf):
        if not self.init():
            return False

        self.cmd(0x24)
        self.data(black_buf)

        self.cmd(0x26)
        self.data(red_buf)

        return self.refresh()


def visible_to_controller_image(img):
    """
    Sichtbares Bild: 296x128 (quer)
    Controller erwartet: 128x296
    Deshalb rotieren wir 90°.
    """
    if img.mode != "1":
        img = img.convert("1")

    if img.size != (DISPLAY_WIDTH, DISPLAY_HEIGHT):
        raise ValueError(f"Bild muss {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} sein")

    # Falls links/rechts später vertauscht sind, hier ROTATE_90 <-> ROTATE_270 wechseln
    return img.transpose(Image.ROTATE_270)


def image_to_buffer_controller(img):
    """
    img muss bereits in Controller-Ausrichtung 128x296 vorliegen.
    """
    if img.mode != "1":
        img = img.convert("1")

    if img.size != (RAM_WIDTH, RAM_HEIGHT):
        raise ValueError(f"Controller-Bild muss {RAM_WIDTH}x{RAM_HEIGHT} sein")

    pixels = img.load()
    buf = []

    bytes_per_line = RAM_WIDTH // 8  # 16

    for y in range(RAM_HEIGHT):
        for xb in range(bytes_per_line):
            byte = 0xFF
            for bit in range(8):
                x = xb * 8 + bit
                if pixels[x, y] == 0:
                    byte &= ~(0x80 >> bit)
            buf.append(byte)

    return buf


def make_test_images():
    black_visible = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
    red_visible = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)

    db = ImageDraw.Draw(black_visible)
    dr = ImageDraw.Draw(red_visible)

    # Rahmen
    db.rectangle((0, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1), outline=0, width=2)

    # Schwarzer Balken links
    db.rectangle((0, 0, 39, DISPLAY_HEIGHT - 1), fill=0)

    # Roter Balken rechts
    dr.rectangle((DISPLAY_WIDTH - 40, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1), fill=0)

    # Weißes Zentrum, damit man die Orientierung klar sieht
    db.rectangle((60, 20, 220, 108), outline=0, width=2)

    try:
        font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font1 = ImageFont.load_default()
        font2 = ImageFont.load_default()

    db.text((80, 30), "GPS", font=font1, fill=0)
    db.text((80, 65), "TRACKER", font=font2, fill=0)
    dr.text((235, 50), "R", font=font1, fill=0)

    black_ctrl = visible_to_controller_image(black_visible)
    red_ctrl = visible_to_controller_image(red_visible)

    black_buf = image_to_buffer_controller(black_ctrl)
    red_buf = image_to_buffer_controller(red_ctrl)

    return black_buf, red_buf


def main():
    print("=" * 60)
    print("2.9 E-PAPER - ROTATION FIX")
    print("=" * 60)
    print(f"Sichtbar:   {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print(f"Controller: {RAM_WIDTH}x{RAM_HEIGHT}")
    print("Pins:")
    print(f"  RST  = GPIO{RST_PIN}")
    print(f"  DC   = GPIO{DC_PIN}")
    print(f"  BUSY = GPIO{BUSY_PIN}")
    print("  CS   = CE0/GPIO8")
    print("=" * 60)

    epd = EPD29()

    try:
        print("\n[1] Weiß löschen...")
        if not epd.clear_white():
            print("❌ Clear fehlgeschlagen")
            return
        time.sleep(2)

        print("\n[2] Testbild senden...")
        black_buf, red_buf = make_test_images()
        if not epd.display(black_buf, red_buf):
            print("❌ Anzeige fehlgeschlagen")
            return

        print("\n✅ Fertig")
        print("Erwartet:")
        print("- links schwarzer Balken")
        print("- rechts roter Balken")
        print("- mittig Text GPS TRACKER")
        print("- keine Streifen")

        epd.sleep()

    except KeyboardInterrupt:
        print("\nAbgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        epd.spi.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()