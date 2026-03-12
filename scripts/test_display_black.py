#!/usr/bin/env python3
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
from waveshare_epd import epd2in9_V2
from PIL import Image, ImageDraw
import time

print("Init Display...")
epd = epd2in9_V2.EPD()
epd.init()

print("Erstelle komplett schwarzes Bild...")
image = Image.new('1', (296, 128), 0)

print("Sende an Display...")
epd.display(epd.getbuffer(image))

print("\nWarte 5 Sekunden - Display sollte KOMPLETT SCHWARZ sein!")
time.sleep(5)

print("\nMache Display komplett weiss...")
image = Image.new('1', (296, 128), 255)
epd.display(epd.getbuffer(image))
time.sleep(5)

epd.sleep()
print("Fertig!")
