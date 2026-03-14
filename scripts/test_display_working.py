#!/usr/bin/env python3
"""
Basierend auf test_display_alive.py (der funktioniert!)
Jetzt mit klarem Muster statt zufälligen Daten
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("="*60)
print("WORKING DISPLAY TEST")
print("="*60)

class WorkingTest:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        GPIO.output(CS_PIN, 0)
        self.spi.xfer2([c])
        GPIO.output(CS_PIN, 1)

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        GPIO.output(CS_PIN, 0)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)
        GPIO.output(CS_PIN, 1)

    def reset(self):
        print("\n1. Hardware Reset...")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def test_clear_pattern(self):
        """Klares Muster - wie alive test aber strukturiert"""
        self.reset()

        print("\n2. Sende klares Schwarz-Weiß-Muster...")

        # Teste 0x24 RAM (hat in frühen Tests funktioniert!)
        print("   Sende zu 0x24 (Schwarz-Buffer)...")
        self.cmd(0x24)

        # Erste 1000 Bytes: KOMPLETT SCHWARZ
        for i in range(1000):
            self.data(0x00)

        # Nächste 1000 Bytes: KOMPLETT WEISS
        for i in range(1000):
            self.data(0xFF)

        # Nächste 1000 Bytes: STREIFEN (0xAA = 10101010)
        for i in range(1000):
            self.data(0xAA)

        # Rest: WEISS
        for i in range(1736):  # 4736 total - 3000 = 1736
            self.data(0xFF)

        print("   Sende zu 0x26 (Rot-Buffer)...")
        self.cmd(0x26)

        # Erste 2000 Bytes: kein Rot
        for i in range(2000):
            self.data(0x00)

        # Nächste 500 Bytes: KOMPLETT ROT
        for i in range(500):
            self.data(0xFF)

        # Rest: kein Rot
        for i in range(2236):  # 4736 total - 2500 = 2236
            self.data(0x00)

        print("\n3. Update mit 0x20...")
        self.cmd(0x20)

        print("   Warte 10 Sekunden (Display aktualisiert)...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n\n   >>> SCHAU AUFS DISPLAY <<<")
        print("   Du solltest sehen:")
        print("   - SCHWARZE Zone")
        print("   - WEISSE Zone")
        print("   - GESTREIFTE Zone (schwarz/weiß)")
        print("   - ROTE Zone")
        print("\n   WO sind die Zonen? (oben/unten/links/rechts)")

    def test_alternative_commands(self):
        """Teste auch 0x10/0x13 Befehle"""
        print("\n\n4. Teste alternative RAM-Befehle (0x10/0x13)...")

        self.reset()
        time.sleep(1)

        print("   Sende zu 0x10 (alternativer Schwarz-Buffer)...")
        self.cmd(0x10)

        # Komplett schwarz
        for i in range(2000):
            self.data(0x00)

        # Rest weiß
        for i in range(2736):
            self.data(0xFF)

        print("   Sende zu 0x13 (alternativer Rot-Buffer)...")
        self.cmd(0x13)

        # Keine Rot
        for i in range(1000):
            self.data(0x00)

        # Rot
        for i in range(1000):
            self.data(0xFF)

        # Kein Rot
        for i in range(2736):
            self.data(0x00)

        print("\n5. Update mit 0x12 (alternativer Update-Befehl)...")
        self.cmd(0x12)

        print("   Warte 10 Sekunden...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            time.sleep(1)

        print("\n\n   >>> SCHAU AUFS DISPLAY <<<")
        print("   Hat sich was geändert?")


try:
    print("\n⚠️  Basiert auf test_display_alive.py (der funktioniert!)")
    print("    Aber mit klaren Mustern statt Zufall\n")

    test = WorkingTest()

    print("\nTEST 1: Befehle 0x24/0x26 mit Update 0x20")
    print("="*60)
    test.test_clear_pattern()

    input("\n\n[ENTER] für Test 2...")

    print("\n\nTEST 2: Befehle 0x10/0x13 mit Update 0x12")
    print("="*60)
    test.test_alternative_commands()

    print("\n\n" + "="*60)
    print("TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWelcher Test hat was Erkennbares gezeigt?")
    print("  Test 1 (0x24/0x26/0x20)")
    print("  Test 2 (0x10/0x13/0x12)")
    print("\nUnd WO waren die Farbblöcke?")
    print("="*60)

    GPIO.cleanup()

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
