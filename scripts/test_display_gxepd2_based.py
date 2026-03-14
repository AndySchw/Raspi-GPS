#!/usr/bin/env python3
"""
GDEW029Z10 Test basierend auf GxEPD2 Arduino Library
Korrekte Init-Sequenz für IL0373 Controller
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# WICHTIG: 128x296 laut GxEPD2!
EPD_WIDTH = 128
EPD_HEIGHT = 296

print("="*60)
print("GDEW029Z10 TEST - GxEPD2 Init-Sequenz")
print("="*60)
print(f"Auflösung: {EPD_WIDTH}x{EPD_HEIGHT}")
print("Controller: IL0373 / UC8151")
print("="*60)

class GDEW029Z10_GxEPD2:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def _writeCommand(self, command):
        GPIO.output(DC_PIN, 0)
        GPIO.output(CS_PIN, 0)
        self.spi.xfer2([command])
        GPIO.output(CS_PIN, 1)

    def _writeData(self, data):
        GPIO.output(DC_PIN, 1)
        GPIO.output(CS_PIN, 0)
        if isinstance(data, int):
            data = [data]
        self.spi.xfer2(data)
        GPIO.output(CS_PIN, 1)

    def _waitWhileBusy(self, message=""):
        if message:
            print(f"  {message}", end='', flush=True)
        timeout = 0
        while GPIO.input(BUSY_PIN) == 0:
            time.sleep(0.01)
            timeout += 1
            if timeout > 1000:  # 10s timeout
                print(" TIMEOUT!")
                return
        if message:
            print(" OK")

    def _reset(self):
        print("\n1. Hardware Reset...")
        GPIO.output(RST_PIN, 0)
        time.sleep(0.01)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.2)

    def init(self):
        """Init-Sequenz basierend auf GxEPD2_290c.cpp"""
        print("2. Initialisierung (GxEPD2-basiert)...")

        self._reset()
        self._waitWhileBusy("Warte nach Reset")

        # Power Setting
        self._writeCommand(0x01)
        self._writeData([0x03, 0x00, 0x2b, 0x2b, 0x09])

        # Booster Soft Start
        self._writeCommand(0x06)
        self._writeData([0x17, 0x17, 0x17])

        # Power On
        self._writeCommand(0x04)
        self._waitWhileBusy("Power On")

        # Panel Setting
        self._writeCommand(0x00)
        self._writeData(0xbf)  # LUT from OTP, B/W mode

        # PLL Control
        self._writeCommand(0x30)
        self._writeData(0x3a)  # 50Hz

        # Resolution Setting
        self._writeCommand(0x61)
        self._writeData([0x80, 0x01, 0x28])  # 128x296

        # VCM DC Setting
        self._writeCommand(0x82)
        self._writeData(0x12)

        # VCOM and Data Interval Setting
        self._writeCommand(0x50)
        self._writeData(0x97)

        print("   ✅ Init abgeschlossen")

    def clearScreen(self):
        """Komplett weiß"""
        print("\n3. Lösche Display (weiß)...")

        bytes_total = int(self.width * self.height / 8)

        # BW RAM
        self._writeCommand(0x10)
        for i in range(bytes_total):
            self._writeData(0xFF)  # Weiß

        # RED RAM
        self._writeCommand(0x13)
        for i in range(bytes_total):
            self._writeData(0x00)  # Kein Rot

        print("4. Display Update...")
        self._writeCommand(0x12)  # Display Refresh
        time.sleep(0.1)
        self._waitWhileBusy("Display Update")
        print("   ✅ Sollte weiß sein!")

    def displayStripes(self):
        """Zeige Streifen-Test"""
        print("\n5. Zeige Streifen-Muster...")

        bytes_total = int(self.width * self.height / 8)

        # BW RAM - Streifen
        self._writeCommand(0x10)

        for i in range(bytes_total):
            if i < 500:
                self._writeData(0x00)  # Schwarz
            elif i < 1000:
                self._writeData(0xFF)  # Weiß
            elif i < 1500:
                self._writeData(0xAA)  # Streifen
            else:
                self._writeData(0xFF)  # Weiß

        # RED RAM - Rote Zone
        self._writeCommand(0x13)

        for i in range(bytes_total):
            if i >= 2000 and i < 2500:
                self._writeData(0xFF)  # Rot
            else:
                self._writeData(0x00)  # Kein Rot

        print("6. Display Update...")
        self._writeCommand(0x12)  # Display Refresh
        time.sleep(0.1)
        self._waitWhileBusy("Display Update")
        print("   ✅ Sollte Streifen zeigen!")

    def sleep(self):
        print("\n7. Deep Sleep...")
        self._writeCommand(0x02)  # Power OFF
        self._waitWhileBusy("Power OFF")

        self._writeCommand(0x07)  # Deep Sleep
        self._writeData(0xA5)


try:
    print("\n⚠️  Basierend auf GxEPD2 Arduino Library!")
    print("    Auflösung: 128x296 (nicht 296x128!)\n")

    epd = GDEW029Z10_GxEPD2()
    epd.init()
    epd.clearScreen()
    time.sleep(3)
    epd.displayStripes()
    epd.sleep()

    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN")
    print("="*60)
    print("\nDu solltest sehen:")
    print("  - Schwarze Zone oben")
    print("  - Weiße Zone")
    print("  - Gestreifte Zone")
    print("  - ROTE Zone")
    print("\nWo sind die Zonen? Vertikal oder horizontal?")
    print("="*60)

except KeyboardInterrupt:
    print("\n\nAbgebrochen")
    GPIO.cleanup()

except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
    GPIO.cleanup()
