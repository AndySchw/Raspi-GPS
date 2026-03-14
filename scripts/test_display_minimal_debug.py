#!/usr/bin/env python3
"""
MINIMAL-TEST für GDEW029Z10
Nur SPI-Kommunikation, keine Bildverarbeitung
"""

import time
import spidev
import RPi.GPIO as GPIO

# Pin-Definitionen
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# Display-Spezifikationen
EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("MINIMAL DEBUG TEST")
print("="*60)

class MinimalEPD:
    def __init__(self):
        print("\n1. Init GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        print("   Pin-Status NACH Setup:")
        print(f"   RST (GPIO{RST_PIN}): {GPIO.input(RST_PIN)}")
        print(f"   DC (GPIO{DC_PIN}): {GPIO.input(DC_PIN)}")
        print(f"   CS (GPIO{CS_PIN}): {GPIO.input(CS_PIN)}")
        print(f"   BUSY (GPIO{BUSY_PIN}): {GPIO.input(BUSY_PIN)}")

        print("\n2. Init SPI...")
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        # SEHR LANGSAMES SPI zum Testen!
        self.spi.max_speed_hz = 500000  # 500 kHz statt 4 MHz
        self.spi.mode = 0  # CPOL=0, CPHA=0

        print(f"   SPI Speed: {self.spi.max_speed_hz} Hz")
        print(f"   SPI Mode: {self.spi.mode}")

    def cmd(self, command):
        """Sende Kommando"""
        GPIO.output(DC_PIN, 0)  # DC=LOW = Command
        GPIO.output(CS_PIN, 0)  # CS aktivieren
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, 1)  # CS deaktivieren

    def data(self, data):
        """Sende Daten"""
        GPIO.output(DC_PIN, 1)  # DC=HIGH = Data
        GPIO.output(CS_PIN, 0)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, 1)

    def check_busy(self):
        """BUSY-Status prüfen ohne zu warten"""
        status = GPIO.input(BUSY_PIN)
        print(f"   BUSY-Pin: {status} ({'HIGH=fertig' if status else 'LOW=beschäftigt'})")
        return status

    def wait_busy(self, timeout_sec=10):
        """Warte auf BUSY mit Timeout"""
        print(f"   Warte auf BUSY (max {timeout_sec}s)...", end='', flush=True)
        start = time.time()
        while GPIO.input(BUSY_PIN) == 0:
            if time.time() - start > timeout_sec:
                print(" TIMEOUT!")
                return False
            time.sleep(0.1)
        elapsed = time.time() - start
        print(f" OK ({elapsed:.1f}s)")
        return True

    def reset(self):
        """Hardware-Reset"""
        print("\n3. Hardware-Reset...")
        print("   RST HIGH")
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

        print("   RST LOW (Reset aktiv)")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.02)

        print("   RST HIGH (Reset beendet)")
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

        self.check_busy()

    def init_display(self):
        """Initialisierung EXAKT aus Datenblatt"""
        print("\n4. Display-Initialisierung...")

        self.reset()

        if not self.wait_busy(timeout_sec=5):
            print("   ⚠️  BUSY hängt nach Reset!")

        print("\n5. SWRESET (0x12)...")
        self.cmd(0x12)
        time.sleep(0.3)

        if not self.wait_busy(timeout_sec=5):
            print("   ⚠️  BUSY hängt nach SWRESET!")

        print("\n6. Driver Output Control (0x01)...")
        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])  # 296 Zeilen

        print("7. Data Entry Mode (0x11)...")
        self.cmd(0x11)
        self.data(0x03)  # X/Y increment

        print("8. Set RAM X (0x44)...")
        self.cmd(0x44)
        self.data([0x00, 0x24])  # 0 bis 36

        print("9. Set RAM Y (0x45)...")
        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

        print("10. Border (0x3C)...")
        self.cmd(0x3C)
        self.data(0x05)

        print("11. Temperature (0x18)...")
        self.cmd(0x18)
        self.data(0x80)

        print("12. Set X counter (0x4E)...")
        self.cmd(0x4E)
        self.data(0x00)

        print("13. Set Y counter (0x4F)...")
        self.cmd(0x4F)
        self.data([0x00, 0x00])

        if not self.wait_busy(timeout_sec=5):
            print("   ⚠️  BUSY hängt nach Init!")

        print("\n   ✅ Init abgeschlossen")

    def test_all_white(self):
        """Test: Alles weiß"""
        print("\n14. Test: Alles WEISS...")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        print(f"   Bytes benötigt: {bytes_total}")

        # Schwarz-Buffer: 0xFF = weiß
        print("   Sende Schwarz-Buffer (0x24)...")
        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)
            if i % 500 == 0:
                print(f"     {i}/{bytes_total}", end='\r', flush=True)
        print(f"     {bytes_total}/{bytes_total} ✓")

        # Rot-Buffer: 0x00 = kein Rot
        print("   Sende Rot-Buffer (0x26)...")
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0x00)
            if i % 500 == 0:
                print(f"     {i}/{bytes_total}", end='\r', flush=True)
        print(f"     {bytes_total}/{bytes_total} ✓")

        # Update
        print("   Display Update (0x20)...")
        self.cmd(0x20)

        if not self.wait_busy(timeout_sec=20):
            print("   ⚠️  BUSY hängt nach Update!")

        print("   ✅ Sollte jetzt KOMPLETT WEISS sein!")

    def test_half_black(self):
        """Test: Hälfte schwarz"""
        print("\n15. Test: Hälfte SCHWARZ, Hälfte WEISS...")

        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)
        half = bytes_total // 2

        # Schwarz-Buffer
        print("   Sende Schwarz-Buffer...")
        self.cmd(0x24)

        # Erste Hälfte: schwarz (0x00)
        for i in range(half):
            self.data(0x00)

        # Zweite Hälfte: weiß (0xFF)
        for i in range(bytes_total - half):
            self.data(0xFF)

        print(f"     {bytes_total} Bytes gesendet")

        # Rot-Buffer: leer
        print("   Sende Rot-Buffer...")
        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0x00)

        # Update
        print("   Display Update (0x20)...")
        self.cmd(0x20)

        if not self.wait_busy(timeout_sec=20):
            print("   ⚠️  BUSY hängt nach Update!")

        print("   ✅ Sollte HALB SCHWARZ, HALB WEISS sein!")

    def sleep(self):
        print("\n16. Sleep-Modus...")
        self.cmd(0x10)
        self.data(0x01)


try:
    epd = MinimalEPD()
    epd.init_display()

    print("\n" + "="*60)
    print("TEST 1: Komplett Weiß")
    print("="*60)
    epd.test_all_white()

    print("\nWarte 5 Sekunden...")
    time.sleep(5)

    print("\n" + "="*60)
    print("TEST 2: Hälfte Schwarz")
    print("="*60)
    epd.test_half_black()

    epd.sleep()

    print("\n" + "="*60)
    print("✅ TESTS ABGESCHLOSSEN")
    print("="*60)
    print("\nWas siehst du?")
    print("  Test 1: Sollte komplett WEISS sein")
    print("  Test 2: Sollte eine Hälfte SCHWARZ, eine WEISS sein")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
