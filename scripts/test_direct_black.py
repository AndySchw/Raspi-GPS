#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24

RAM_WIDTH = 128
RAM_HEIGHT = 296
TOTAL_BYTES = (RAM_WIDTH // 8) * RAM_HEIGHT  # 4736

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 200000
spi.mode = 0

def cmd(c):
    GPIO.output(DC_PIN, 0)
    spi.xfer2([c])

def data(d):
    GPIO.output(DC_PIN, 1)
    if isinstance(d, int):
        spi.xfer2([d])
    else:
        chunk = 512
        d = list(d)
        for i in range(0, len(d), chunk):
            spi.xfer2(d[i:i+chunk])

def wait_idle(timeout=10):
    start = time.time()
    while GPIO.input(BUSY_PIN) == 0:   # 0=busy, 1=idle
        if time.time() - start > timeout:
            print("❌ Timeout BUSY")
            return False
        time.sleep(0.05)
    return True

def reset():
    GPIO.output(RST_PIN, 0)
    time.sleep(0.2)
    GPIO.output(RST_PIN, 1)
    time.sleep(0.2)

def set_cursor():
    cmd(0x4E)
    data(0x00)
    cmd(0x4F)
    data([0x00, 0x00])

def init():
    reset()
    wait_idle(5)

    cmd(0x12)   # SWRESET
    time.sleep(0.2)
    wait_idle(5)

    cmd(0x01)
    data([0x27, 0x01, 0x00])   # 296 lines

    cmd(0x11)
    data(0x03)

    cmd(0x44)
    data([0x00, 0x0F])         # 128 px / 8 = 16 bytes

    cmd(0x45)
    data([0x00, 0x00, 0x27, 0x01])

    cmd(0x3C)
    data(0x05)

    cmd(0x18)
    data(0x80)

    set_cursor()
    wait_idle(5)

try:
    print("Init...")
    init()

    print("Weiss in beide Buffer...")
    set_cursor()
    cmd(0x24)
    for _ in range(TOTAL_BYTES):
        data(0xFF)

    set_cursor()
    cmd(0x26)
    for _ in range(TOTAL_BYTES):
        data(0xFF)

    print("Refresh Weiss...")
    cmd(0x20)
    wait_idle(10)
    time.sleep(2)

    print("Schwarz-Buffer voll schwarz...")
    set_cursor()
    cmd(0x24)
    for _ in range(TOTAL_BYTES):
        data(0x00)

    set_cursor()
    cmd(0x26)
    for _ in range(TOTAL_BYTES):
        data(0xFF)

    print("Refresh Schwarz...")
    cmd(0x20)
    wait_idle(10)

    print("Fertig")
finally:
    spi.close()
    GPIO.cleanup()