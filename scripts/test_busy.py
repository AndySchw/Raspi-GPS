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

print("BUSY vor Reset:", GPIO.input(BUSY_PIN))

GPIO.output(RST_PIN, 0)
time.sleep(0.2)
print("BUSY waehrend Reset low:", GPIO.input(BUSY_PIN))

GPIO.output(RST_PIN, 1)
time.sleep(0.2)
print("BUSY nach Reset high:", GPIO.input(BUSY_PIN))

for i in range(20):
    print("BUSY", i, "=", GPIO.input(BUSY_PIN))
    time.sleep(0.2)

GPIO.cleanup()