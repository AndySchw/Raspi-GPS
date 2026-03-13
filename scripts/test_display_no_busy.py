#!/usr/bin/env python3
"""
Test für 2.9" Rot/Schwarz Display OHNE BUSY-Pin
Nutzt feste Wartezeiten statt BUSY-Check
"""
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
from waveshare_epd import epd2in9b_V4
from PIL import Image, ImageDraw, ImageFont
import time

print("="*60)
print("Display-Test OHNE BUSY-Pin")
print("="*60)

# Monkey-Patch: Überschreibe ReadBusy mit fester Wartezeit
original_readbusy = epd2in9b_V4.EPD.ReadBusy

def dummy_readbusy(self):
    """Warte feste Zeit statt BUSY zu checken"""
    time.sleep(0.2)  # 200ms Wartezeit

epd2in9b_V4.EPD.ReadBusy = dummy_readbusy

print("\n1. Initialisiere Display (ohne BUSY-Check)...")
epd = epd2in9b_V4.EPD()
epd.init()
print("   ✅ Init OK")

print("\n2. Lösche Display...")
epd.Clear()
time.sleep(3)  # Warte 3 Sekunden für Clear
print("   ✅ Display gelöscht")

print("\n3. Erstelle Test-Bild...")
# Zwei separate Bilder: Schwarz und Rot
black_image = Image.new('1', (epd.height, epd.width), 255)
red_image = Image.new('1', (epd.height, epd.width), 255)

draw_black = ImageDraw.Draw(black_image)
draw_red = ImageDraw.Draw(red_image)

# Große schwarze Box oben
draw_black.rectangle((5, 5, 123, 60), fill=0, outline=0)

# Große rote Box unten
draw_red.rectangle((5, 70, 123, 125), fill=0, outline=0)

# Text
try:
    font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw_black.text((10, 15), "GPS", font=font_large, fill=255)  # Weiß auf Schwarz
draw_red.text((10, 80), "ANDY", font=font_large, fill=255)   # Weiß auf Rot

print("   ✅ Bild erstellt")

print("\n4. Sende an Display...")
epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
print("   ✅ Gesendet")

print("\n5. Warte 15 Sekunden (Display aktualisiert sich)...")
print("\n   >>> SCHAU AUFS DISPLAY <<<")
print("   Du solltest sehen:")
print("     - SCHWARZE Box oben mit weißem 'GPS'")
print("     - ROTE Box unten mit weißem 'ANDY'")

for i in range(15, 0, -1):
    print(f"   {i}...", end='\r', flush=True)
    time.sleep(1)

print("\n\n6. Sleep-Modus...")
epd.sleep()
print("   ✅ Fertig!")

print("\n" + "="*60)
print("Hat das Display was angezeigt?")
print("Das Bild bleibt auch nach dem Ausschalten sichtbar (ePaper!)")
print("="*60)
