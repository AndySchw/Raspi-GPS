#!/usr/bin/env python3
import sys
sys.path.append('/home/gpsandy/gps_device/lib')

from waveshare_epd import epd2in9_V2
from PIL import Image, ImageDraw, ImageFont
import time

print("Initialisiere Display...")
epd = epd2in9_V2.EPD()

print("Init...")
epd.init()

print("Clear Display (schwarz)...")
epd.Clear(0x00)  # Schwarz
time.sleep(2)

print("Clear Display (weiß)...")
epd.Clear(0xFF)  # Weiß
time.sleep(2)

print("Zeichne schwarzes Rechteck...")
image = Image.new('1', (epd.width, epd.height), 255)
draw = ImageDraw.Draw(image)
draw.rectangle((10, 10, 100, 100), fill=0, outline=0)
epd.display(epd.getbuffer(image))

print("Fertig! Display sollte schwarzes Rechteck zeigen.")
print("Drücke Ctrl+C zum Beenden...")
time.sleep(10)

epd.sleep()
