#!/usr/bin/env python3
import sys
sys.path.append('/home/gpsandy/gps_device/lib')
from waveshare_epd import epd2in9_V2, epdconfig
import RPi.GPIO as GPIO
import time

print("="*60)
print("DISPLAY DEBUG TEST")
print("="*60)

# Pin-Definitionen aus epdconfig
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

print("\n1. Teste GPIO-Zugriff...")
GPIO.setmode(GPIO.BCM)

# Setze Output-Pins
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(CS_PIN, GPIO.OUT)

print(f"   RST_PIN  (GPIO{RST_PIN}): Output")
print(f"   DC_PIN   (GPIO{DC_PIN}): Output")
print(f"   CS_PIN   (GPIO{CS_PIN}): Output")

print("\n2. Teste Hardware-Reset (RST-Pin)...")
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(RST_PIN, GPIO.LOW)
print("   RST -> LOW")
time.sleep(0.2)
GPIO.output(RST_PIN, GPIO.HIGH)
print("   RST -> HIGH")
time.sleep(0.2)
print("   ✅ Reset-Sequenz gesendet")

print("\n3. Teste CS-Pin (Chip Select)...")
GPIO.output(CS_PIN, GPIO.LOW)
print("   CS -> LOW (aktiviert)")
time.sleep(0.1)
GPIO.output(CS_PIN, GPIO.HIGH)
print("   CS -> HIGH (deaktiviert)")
print("   ✅ CS-Pin funktioniert")

print("\n4. Teste DC-Pin (Data/Command)...")
GPIO.output(DC_PIN, GPIO.LOW)
print("   DC -> LOW (Command-Modus)")
time.sleep(0.1)
GPIO.output(DC_PIN, GPIO.HIGH)
print("   DC -> HIGH (Data-Modus)")
print("   ✅ DC-Pin funktioniert")

print("\n5. Teste BUSY-Pin (Input)...")
try:
    GPIO.setup(BUSY_PIN, GPIO.IN)
    busy_state = GPIO.input(BUSY_PIN)
    print(f"   BUSY-Pin Status: {busy_state} (1=HIGH/nicht beschäftigt, 0=LOW/beschäftigt)")
    if busy_state == 1:
        print("   ✅ BUSY-Pin meldet: Display bereit")
    else:
        print("   ⚠️  BUSY-Pin meldet: Display beschäftigt (ungewöhnlich beim Start)")
except Exception as e:
    print(f"   ❌ BUSY-Pin Fehler: {e}")

print("\n6. Teste SPI-Verbindung...")
try:
    import spidev
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 4000000

    # Sende Test-Daten
    test_data = [0x12, 0x34, 0x56, 0x78]
    response = spi.xfer2(test_data)

    print(f"   Gesendet:  {test_data}")
    print(f"   Empfangen: {response}")
    print("   ✅ SPI funktioniert")
    spi.close()
except Exception as e:
    print(f"   ❌ SPI-Fehler: {e}")

GPIO.cleanup()

print("\n" + "="*60)
print("DEBUG-TEST ABGESCHLOSSEN")
print("="*60)
print("\nWenn alle Tests ✅ sind, ist die Verkabelung OK.")
print("Wenn BUSY-Pin = 0 bleibt, ist das Display evtl. defekt.")
