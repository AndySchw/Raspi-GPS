#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO

# =========================
# PINBELEGUNG
# =========================
RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
# CS = GPIO8 / CE0 über spidev

# =========================
# CONTROLLER-GROESSE
# =========================
RAM_WIDTH = 128
RAM_HEIGHT = 296
BYTES_PER_LINE = RAM_WIDTH // 8   # 16
TOTAL_BYTES = BYTES_PER_LINE * RAM_HEIGHT  # 4736

class EPDTest:
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
            chunk = 512
            d = list(d)
            for i in range(0, len(d), chunk):
                self.spi.xfer2(d[i:i + chunk])

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def wait_idle(self, timeout=10):
        start = time.time()
        # Laut PDF: BUSY high aktiv -> 1 = busy, 0 = idle
        while GPIO.input(BUSY_PIN) == 1:
            if time.time() - start > timeout:
                print("❌ Timeout: Display bleibt busy")
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

        # X: 0..15 (16 Bytes = 128 Pixel)
        self.cmd(0x44)
        self.data([0x00, 0x0F])

        # Y: 0..295
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x27, 0x01])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temp sensor
        self.data(0x80)

        self.set_cursor(0, 0)

        print("✅ Init OK")
        return True

    def refresh_v1(self):
        print("Refresh V1: nur 0x20")
        self.cmd(0x20)
        return self.wait_idle(10)

    def refresh_v2(self):
        print("Refresh V2: 0x22 + 0x20")
        self.cmd(0x22)
        self.data(0xF7)
        self.cmd(0x20)
        return self.wait_idle(10)

    def write_bw_buffer(self, value):
        self.set_cursor(0, 0)
        self.cmd(0x24)
        for _ in range(TOTAL_BYTES):
            self.data(value)

    def write_red_buffer(self, value):
        self.set_cursor(0, 0)
        self.cmd(0x26)
        for _ in range(TOTAL_BYTES):
            self.data(value)

    def full_white(self, refresh_mode=1):
        print("\n=== TEST: FULL WHITE ===")
        if not self.init():
            return False

        self.write_bw_buffer(0xFF)
        self.write_red_buffer(0xFF)

        if refresh_mode == 1:
            return self.refresh_v1()
        return self.refresh_v2()

    def full_black(self, refresh_mode=1):
        print("\n=== TEST: FULL BLACK ===")
        if not self.init():
            return False

        self.write_bw_buffer(0x00)
        self.write_red_buffer(0xFF)

        if refresh_mode == 1:
            return self.refresh_v1()
        return self.refresh_v2()

    def full_red(self, refresh_mode=1):
        print("\n=== TEST: FULL RED ===")
        if not self.init():
            return False

        self.write_bw_buffer(0xFF)
        self.write_red_buffer(0x00)

        if refresh_mode == 1:
            return self.refresh_v1()
        return self.refresh_v2()

    def bars(self, refresh_mode=1):
        print("\n=== TEST: BARS ===")
        if not self.init():
            return False

        # Schwarz links
        self.set_cursor(0, 0)
        self.cmd(0x24)
        for y in range(RAM_HEIGHT):
            for xb in range(BYTES_PER_LINE):
                if xb < 4:
                    self.data(0x00)
                else:
                    self.data(0xFF)

        # Rot rechts
        self.set_cursor(0, 0)
        self.cmd(0x26)
        for y in range(RAM_HEIGHT):
            for xb in range(BYTES_PER_LINE):
                if xb >= BYTES_PER_LINE - 4:
                    self.data(0x00)
                else:
                    self.data(0xFF)

        if refresh_mode == 1:
            return self.refresh_v1()
        return self.refresh_v2()

    def close(self):
        self.spi.close()
        GPIO.cleanup()


def main():
    epd = EPDTest()
    try:
        print("=" * 60)
        print("2.9 E-PAPER MINIMALTEST")
        print("=" * 60)
        print("Pins:")
        print(f"RST  = GPIO{RST_PIN}")
        print(f"DC   = GPIO{DC_PIN}")
        print(f"BUSY = GPIO{BUSY_PIN}")
        print("CS   = GPIO8 / CE0")
        print("=" * 60)

        print("\n--- RUNDE 1: Refresh V1 ---")
        epd.full_white(refresh_mode=1)
        time.sleep(3)

        epd.full_black(refresh_mode=1)
        time.sleep(3)

        epd.full_red(refresh_mode=1)
        time.sleep(3)

        epd.bars(refresh_mode=1)
        time.sleep(5)

        print("\n--- RUNDE 2: Refresh V2 ---")
        epd.full_white(refresh_mode=2)
        time.sleep(3)

        epd.full_black(refresh_mode=2)
        time.sleep(3)

        epd.full_red(refresh_mode=2)
        time.sleep(3)

        epd.bars(refresh_mode=2)
        time.sleep(5)

        print("\n✅ Test fertig")
        print("Bitte notieren:")
        print("1. Wurde weiß sichtbar?")
        print("2. Wurde schwarz sichtbar?")
        print("3. Wurde rot sichtbar?")
        print("4. Welche Refresh-Runde hat reagiert? V1 oder V2?")

    finally:
        epd.close()


if __name__ == "__main__":
    main()