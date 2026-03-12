#!/usr/bin/env python3
"""
Display-Test für Waveshare 2.9inch e-Paper Module (296x128)
Rev2.1, schwarz/weiß

Zeigt Test-Text und Grafiken auf dem Display an.
"""

import sys
import os
from pathlib import Path

# Füge src/ zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

# Waveshare Library-Pfad
epd_path = Path.home() / 'gps_device/e-Paper/RaspberryPi_JetsonNano/python/lib'
if epd_path.exists():
    sys.path.append(str(epd_path))

try:
    from waveshare_epd import epd2in9_V2
    from PIL import Image, ImageDraw, ImageFont
    import time
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("\nBitte installiere die Waveshare Library:")
    print("  cd ~/gps_device")
    print("  git clone https://github.com/waveshare/e-Paper.git")
    print("  cd e-Paper/RaspberryPi_JetsonNano/python/")
    print("  sudo python3 setup.py install")
    sys.exit(1)


def test_display():
    """Testet das ePaper Display"""

    print("=" * 60)
    print("DISPLAY-TEST: Waveshare 2.9inch e-Paper Rev2.1")
    print("=" * 60)

    try:
        # Display initialisieren
        print("\n1. Initialisiere Display...")
        epd = epd2in9_V2.EPD()
        epd.init()
        epd.Clear(0xFF)  # Weiß
        time.sleep(1)

        print("   ✅ Display initialisiert")

        # Bild erstellen (296x128, schwarz/weiß)
        print("\n2. Erstelle Bild...")
        image = Image.new('1', (epd.width, epd.height), 255)  # 255 = weiß
        draw = ImageDraw.Draw(image)

        # Font laden (System-Font)
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
        except:
            print("   ⚠️  TrueType-Fonts nicht gefunden, nutze Standard-Font")
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Rahmen zeichnen
        draw.rectangle((0, 0, epd.width-1, epd.height-1), outline=0)

        # Titel
        draw.text((10, 10), "GPS-GERÄT", font=font_large, fill=0)
        draw.line((10, 40, epd.width-10, 40), fill=0, width=2)

        # Status-Infos
        draw.text((10, 50), "Hardware-Test:", font=font_medium, fill=0)
        draw.text((20, 70), "✓ Display OK", font=font_small, fill=0)
        draw.text((20, 85), "✓ I²C OK (2 Geräte)", font=font_small, fill=0)
        draw.text((20, 100), "✓ GPS OK (UART)", font=font_small, fill=0)

        print("   ✅ Bild erstellt")

        # Auf Display anzeigen
        print("\n3. Zeige Bild auf Display...")
        epd.display(epd.getbuffer(image))
        print("   ✅ Bild angezeigt")

        print("\n4. Display bleibt 10 Sekunden an...")
        time.sleep(10)

        # Display in Sleep-Modus
        print("\n5. Versetze Display in Sleep-Modus...")
        epd.sleep()
        print("   ✅ Display im Sleep-Modus")

        print("\n" + "=" * 60)
        print("🎉 DISPLAY-TEST ERFOLGREICH!")
        print("=" * 60)
        print("\nDas Display sollte jetzt Text anzeigen.")
        print("Es bleibt sichtbar auch wenn der Pi aus ist (ePaper!)")

        return 0

    except IOError as e:
        print(f"\n❌ I/O-Fehler: {e}")
        print("\nMögliche Ursachen:")
        print("  - SPI nicht aktiviert (sudo raspi-config)")
        print("  - Display nicht richtig angeschlossen")
        print("  - Falsche Pins")
        return 1

    except KeyboardInterrupt:
        print("\n\nTest abgebrochen")
        epd.epdconfig.module_exit()
        return 1

    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


def clear_display():
    """Löscht das Display (macht es komplett weiß)"""
    print("Lösche Display...")
    try:
        epd = epd2in9_V2.EPD()
        epd.init()
        epd.Clear(0xFF)
        epd.sleep()
        print("✅ Display gelöscht")
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_display()
    else:
        sys.exit(test_display())
