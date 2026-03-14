#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24

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

def wait_idle(label, timeout=5):
    print(f"{label} BUSY={GPIO.input(BUSY_PIN)}")
    start = time.time()
    while GPIO.input(BUSY_PIN) == 0:   # 0 = busy
        if time.time() - start > timeout:
            print("❌ Timeout - BUSY bleibt 0")
            return False
        time.sleep(0.05)
    print("✅ Display idle")
    return True

print("Start BUSY:", GPIO.input(BUSY_PIN))

print("\nHardware Reset...")
GPIO.output(RST_PIN, 0)
time.sleep(0.2)
GPIO.output(RST_PIN, 1)

wait_idle("Nach Reset")

print("\nSoftware Reset senden...")
cmd(0x12)

wait_idle("Nach SWRESET")

spi.close()
GPIO.cleanup()
print("\nFertig")