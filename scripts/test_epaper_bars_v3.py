#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

# =========================
# PINS
# =========================
RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
# CS = CE0 / GPIO8 über spidev

# =========================
# SICHTBARE DISPLAY-GROESSE
# =========================
DISPLAY_WIDTH = 296
DISPLAY_HEIGHT = 128

# =========================
# CONTROLLER-RAM-GROESSE
# =========================
RAM_WIDTH = 128
RAM_HEIGHT = 296
BYTES_PER_LINE = RAM_WIDTH // 8
TOTAL_BYTES = BYTES_PER_LINE * RAM_HEIGHT

class EPD29Test:
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
            return

        d = list(d)
        chunk_size = 512
        for i in range(0, len(d), chunk_size):
            self.spi.xfer2(d[i:i + chunk_size])

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def wait_idle(self, timeout=10):
        start = time.time()
        # Für DEIN Board gilt nach den Tests:
        # 0 = busy, 1 = idle
        while GPIO.input(BUSY_PIN) == 0:
            if time.time() - start > timeout:
                print("❌ Timeout: BUSY bleibt 0")
                return False
            time.sleep(0.05)
        return True

    def set_cursor(self, x_byte=0, y=0):
        self.cmd(0x4E)
        self.data(x_byte)
        self.cmd(0x4F)
        self.data([y & 0xFF, (y >> 8) & 0xFF])

    def init(self):
        print("Initialisiere Display...")
        self.reset()

        if not self.wait_idle(5):
            return False

        self.cmd(0x12)  # SWRESET
        time.sleep(0.2)

        if not self.wait_idle(5):
            return False

        # Driver output control: 296 Zeilen
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        # Data entry mode
        self.cmd(0x11)
        self.data(0x03)

        # RAM X: 128 Pixel => 16 Bytes => 0x0F
        self.cmd(0x44)
        self.data([0x00, 0x0F])

        # RAM Y: 296 Zeilen => 0x0127
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temp sensor
        self.data(0x80)

        self.set_cursor(0, 0)

        print("✅ Init OK")
        return True

    def refresh(self):
        # Alternative Refresh-Sequenz
        self.cmd(0x22)
        self.data(0xF7)
        self.cmd(0x20)
        return self.wait_idle(15)

    def clear_white(self):
        if not self.init():
            return False

        self.set_cursor(0, 0)
        self.cmd(0x24)
        for _ in range(TOTAL_BYTES):
            self.data(0xFF)

        self.set_cursor(0, 0)
        self.cmd(0x26)
        for _ in range(TOTAL_BYTES):
            self.data(0xFF)

        return self.refresh()

    def display_buffers(self, black_buf, red_buf):
        if len(black_buf) != TOTAL_BYTES or len(red_buf) != TOTAL_BYTES:
            raise ValueError(
                f"Buffergröße falsch: erwartet {TOTAL_BYTES}, "
                f"black={len(black_buf)}, red={len(red_buf)}"
            )

        if not self.init():
            return False

        self.set_cursor(0, 0)
        self.cmd(0x24)
        for b in black_buf:
            self.data(b)

        self.set_cursor(0, 0)
        self.cmd(0x26)
        for b in red_buf:
            self.data(b)

        return self.refresh()

    def sleep(self):
        self.cmd(0x10)
        self.data(0x01)
        time.sleep(0.1)

    def close(self):
        self.spi.close()
        GPIO.cleanup()


def visible_to_controller(img):
    """
    Sichtbares Bild: 296x128
    Controller erwartet: 128x296
    """
    if img.mode != "1":
        img = img.convert("1")
    return img.transpose(Image.ROTATE_270)


def controller_image_to_buffer(img):
    if img.mode != "1":
        img = img.convert("1")

    if img.size != (RAM_WIDTH, RAM_HEIGHT):
        raise ValueError(f"Controller-Bild muss {RAM_WIDTH}x{RAM_HEIGHT} sein")

    pixels = img.load()
    buf = []

    for y in range(RAM_HEIGHT):
        for xb in range(BYTES_PER_LINE):
            byte = 0xFF
            for bit in range(8):
                x = xb * 8 + bit
                if pixels[x, y] == 0:
                    byte &= ~(0x80 >> bit)
            buf.append(byte)

    return buf


def build_test_bars():
    # Sichtbares Wunschbild
    black_visible = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)
    red_visible = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)

    db = ImageDraw.Draw(black_visible)
    dr = ImageDraw.Draw(red_visible)

    # Links schwarzer Balken
    db.rectangle((0, 0, 49, DISPLAY_HEIGHT - 1), fill=0)

    # Rechts roter Balken
    dr.rectangle((DISPLAY_WIDTH - 50, 0, DISPLAY_WIDTH - 1, DISPLAY_HEIGHT - 1), fill=0)

    # In der Mitte ein weißer Bereich lassen, damit man die Richtung gut erkennt

    # In Controller-Ausrichtung umwandeln
    black_ctrl = visible_to_controller(black_visible)
    red_ctrl = visible_to_controller(red_visible)

    black_buf = controller_image_to_buffer(black_ctrl)
    red_buf = controller_image_to_buffer(red_ctrl)

    return black_buf, red_buf


def main():
    print("=" * 60)
    print("2.9 E-PAPER BARS TEST V3")
    print("=" * 60)
    print("Ziel:")
    print("- links schwarzer Balken")
    print("- rechts roter Balken")
    print("- Mitte weiss")
    print("=" * 60)

    epd = EPD29Test()

    try:
        print("\n[1] Clear White...")
        if not epd.clear_white():
            print("❌ Clear fehlgeschlagen")
            return
        time.sleep(2)

        print("\n[2] Erzeuge Balken-Testbild...")
        black_buf, red_buf = build_test_bars()

        print("\n[3] Sende Bild...")
        if not epd.display_buffers(black_buf, red_buf):
            print("❌ Bildanzeige fehlgeschlagen")
            return

        print("\n✅ Fertig")
        print("Bitte prüfen:")
        print("1. Links schwarz?")
        print("2. Rechts rot?")
        print("3. Mitte weiss?")
        print("4. Noch Streifen oder nichts?")

        epd.sleep()

    except KeyboardInterrupt:
        print("\nAbgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        epd.close()


if __name__ == "__main__":
    main()