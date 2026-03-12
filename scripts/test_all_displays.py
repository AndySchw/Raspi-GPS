#!/usr/bin/env python3
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
import time

# Probiere verschiedene Treiber
drivers = ['epd2in9_V2', 'epd2in9', 'epd2in9d', 'epd2in9bc']

for driver_name in drivers:
    try:
        print(f"\n{'='*60}")
        print(f"Teste {driver_name}")
        print('='*60)

        epd_module = __import__(f'waveshare_epd.{driver_name}', fromlist=['EPD'])
        epd = epd_module.EPD()

        print("  Init...")
        epd.init()
        print("  ✅ Init OK")

        print("\n  Mache Display SCHWARZ...")
        epd.Clear(0x00)
        print("  >>> SCHAU AUFS DISPLAY - IST ES SCHWARZ? <<<")
        time.sleep(5)

        print("\n  Mache Display WEISS...")
        epd.Clear(0xFF)
        print("  >>> SCHAU AUFS DISPLAY - IST ES WEISS? <<<")
        time.sleep(5)

        epd.sleep()
        print(f"\n✅ {driver_name} Test abgeschlossen")

        answer = input("\nHat das Display was angezeigt? (j/n): ")
        if answer.lower() == 'j':
            print(f"\n🎉 SUPER! Der richtige Treiber ist: {driver_name}")
            break
        else:
            print("  Probiere nächsten Treiber...\n")

    except Exception as e:
        print(f"❌ {driver_name} Fehler: {e}")
        print("  Probiere nächsten Treiber...\n")

print("\nTest beendet.")
