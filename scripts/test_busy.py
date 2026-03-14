#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
BUSY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

GPIO.output(RST_PIN, 1)
GPIO.output(DC_PIN, 1)

print("Starte Pin-Test...")
for i in range(20):
    print(f"{i:02d} BUSY={GPIO.input(BUSY_PIN)}")
    time.sleep(0.2)

print("RST LOW")
GPIO.output(RST_PIN, 0)
for i in range(10):
    print(f"RST low {i:02d} BUSY={GPIO.input(BUSY_PIN)}")
    time.sleep(0.2)

print("RST HIGH")
GPIO.output(RST_PIN, 1)
for i in range(20):
    print(f"RST high {i:02d} BUSY={GPIO.input(BUSY_PIN)}")
    time.sleep(0.2)

GPIO.cleanup()