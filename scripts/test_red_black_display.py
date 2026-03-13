#!/usr/bin/env python3
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
import time

# Probiere die 3-Farben-Treiber (schwarz/weiß/rot)
drivers = ['epd2in9b_V4', 'epd2in9b_V3', 'epd2in9bc']

for driver_name in drivers:
    try:
        print(f"\n{'='*60}")
        print(f"Teste {driver_name} (Rot/Schwarz Display)")
        print('='*60)

        epd_module = __import__(f'waveshare_epd.{driver_name}', fromlist=['EPD'])
        epd = epd_module.EPD()

        print("  Init...")
        epd.init()
        print("  ✅ Init OK")

        print("\n  Lösche Display...")
        epd.Clear()
        time.sleep(2)

        print("\n  Zeige Test-Bild (Schwarz + Rot)...")
        from PIL import Image, ImageDraw, ImageFont

        # Zwei separate Bilder: eins für Schwarz, eins für Rot
        Himage_black = Image.new('1', (epd.height, epd.width), 255)  # Weiß
        Himage_red = Image.new('1', (epd.height, epd.width), 255)    # Weiß

        draw_black = ImageDraw.Draw(Himage_black)
        draw_red = ImageDraw.Draw(Himage_red)

        # Schwarzes Rechteck oben
        draw_black.rectangle((10, 10, 100, 60), fill=0)

        # Rotes Rechteck unten
        draw_red.rectangle((10, 70, 100, 120), fill=0)

        # Text
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        except:
            font = ImageFont.load_default()

        draw_black.text((110, 20), "SCHWARZ", font=font, fill=0)
        draw_red.text((110, 80), "ROT", font=font, fill=0)

        print("  Sende Daten an Display...")
        epd.display(epd.getbuffer(Himage_black), epd.getbuffer(Himage_red))

        print("\n  >>> SCHAU AUFS DISPLAY <<<")
        print("  Du solltest sehen:")
        print("    - Schwarzes Rechteck oben + Text 'SCHWARZ'")
        print("    - ROTES Rechteck unten + Text 'ROT'")

        time.sleep(10)

        epd.sleep()
        print(f"\n✅ {driver_name} Test abgeschlossen")

        answer = input("\nHat das Display SCHWARZ + ROT angezeigt? (j/n): ")
        if answer.lower() == 'j':
            print(f"\n🎉 SUPER! Der richtige Treiber ist: {driver_name}")
            print(f"\nDas Display ist ein 3-Farben ePaper (Schwarz/Weiß/Rot)!")
            break
        else:
            print("  Probiere nächsten Treiber...\n")

    except Exception as e:
        print(f"❌ {driver_name} Fehler: {e}")
        import traceback
        traceback.print_exc()
        print("  Probiere nächsten Treiber...\n")

print("\nTest beendet.")
