#!/usr/bin/env python3
"""
Finaler Display-Test mit GPS-Motiv
Zeigt "GPS ANDY" in Schwarz/Rot
"""
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
from waveshare_epd import epd2in9b_V4
from PIL import Image, ImageDraw, ImageFont
import time

print("="*60)
print("GPS-GERÄT DISPLAY TEST")
print("="*60)

# Monkey-Patch für BUSY
def dummy_readbusy(self):
    time.sleep(0.3)

epd2in9b_V4.EPD.ReadBusy = dummy_readbusy

print("\n1. Init Display...")
epd = epd2in9b_V4.EPD()
epd.init()
print("   ✅ OK")

print("\n2. Clear Display (dauert ~15 Sekunden)...")
epd.Clear()
time.sleep(15)  # Warte länger für vollständiges Clear
print("   ✅ OK - Display sollte jetzt WEIß sein")

print("\n3. Erstelle GPS-Bild...")

# 128 (höhe) x 296 (breite) - Display ist gedreht
black_img = Image.new('1', (128, 296), 255)
red_img = Image.new('1', (128, 296), 255)

draw_black = ImageDraw.Draw(black_img)
draw_red = ImageDraw.Draw(red_img)

# Fonts
try:
    font_huge = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
except:
    font_huge = ImageFont.load_default()
    font_large = ImageFont.load_default()

# Großer schwarzer Rahmen
draw_black.rectangle((2, 2, 126, 294), outline=0, width=3)

# Text SCHWARZ
draw_black.text((20, 40), "GPS", font=font_huge, fill=0)

# Text ROT
draw_red.text((15, 110), "ANDY", font=font_large, fill=0)

# Kleine schwarze Box als Marker
draw_black.rectangle((10, 200, 50, 240), fill=0)

# Kleine rote Box als Marker
draw_red.rectangle((70, 200, 110, 240), fill=0)

print("   ✅ Bild erstellt")

print("\n4. Sende an Display (dauert ~20 Sekunden)...")
epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))

print("\n5. Warte auf Display-Refresh...")
print("   Das Display sollte jetzt blinken/flackern!")
print("   Das ist normal bei ePaper!")

for i in range(20, 0, -1):
    print(f"   Noch {i} Sekunden...", end='\r', flush=True)
    time.sleep(1)

print("\n\n6. Sleep...")
epd.sleep()

print("\n" + "="*60)
print("FERTIG!")
print("="*60)
print("\nDu solltest jetzt sehen:")
print("  - Schwarzen Rahmen")
print("  - 'GPS' in SCHWARZ (groß)")
print("  - 'ANDY' in ROT")
print("  - Eine schwarze und eine rote Box unten")
print("\nDas Bild bleibt auch beim Ausschalten!")
print("="*60)
