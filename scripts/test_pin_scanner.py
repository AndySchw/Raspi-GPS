#!/usr/bin/env python3
"""
SYSTEMATISCHER PIN-SCANNER
Testet alle möglichen Pin-Kombinationen für RST, DC, BUSY

ACHTUNG: Dieses Script dauert lange! Aber es findet die richtige Kombination.
"""

import time
import spidev
import RPi.GPIO as GPIO
import itertools

# SPI-Pins sind fest (hardware-gebunden)
# MOSI = GPIO10 (Pin 19)
# SCLK = GPIO11 (Pin 23)
# CE0  = GPIO8  (Pin 24) - wird von spidev gesteuert

# Diese Pins könnten RST, DC, oder BUSY sein
CANDIDATE_PINS = [17, 24, 25]  # Die drei Pins die wir verdrahtet haben

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("SYSTEMATISCHER PIN-SCANNER")
print("="*60)
print(f"Teste alle Kombinationen von: {CANDIDATE_PINS}")
print("Das kann einige Minuten dauern...")
print("="*60)

class PinTester:
    def __init__(self, rst_pin, dc_pin, busy_pin):
        self.rst_pin = rst_pin
        self.dc_pin = dc_pin
        self.busy_pin = busy_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup
        GPIO.setup(rst_pin, GPIO.OUT)
        GPIO.setup(dc_pin, GPIO.OUT)
        GPIO.setup(busy_pin, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(self.dc_pin, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(self.dc_pin, 1)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)

    def reset(self):
        GPIO.output(self.rst_pin, 0)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, 1)
        time.sleep(0.2)

    def check_busy(self):
        """Checke BUSY-Pin vor und nach Reset"""
        busy_before = GPIO.input(self.busy_pin)
        self.reset()
        time.sleep(0.5)
        busy_after = GPIO.input(self.busy_pin)
        return busy_before, busy_after

    def test_clear_white(self):
        """Versuche Display weiß zu machen"""
        try:
            self.reset()
            time.sleep(0.3)

            # Software Reset
            self.cmd(0x12)
            time.sleep(0.3)

            # Init-Sequenz (minimal)
            self.cmd(0x01)  # Driver Output
            self.data([0x27, 0x01, 0x00])

            self.cmd(0x11)  # Data Entry Mode
            self.data(0x03)

            self.cmd(0x44)  # RAM X
            self.data([0x00, 0x24])  # 0 bis 0x24 (37 bytes)

            self.cmd(0x45)  # RAM Y
            self.data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

            # Clear white
            bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

            self.cmd(0x24)  # Black buffer
            for i in range(bytes_total):
                self.data(0xFF)

            self.cmd(0x26)  # Red buffer
            for i in range(bytes_total):
                self.data(0xFF)

            # Update
            self.cmd(0x20)
            time.sleep(2)  # Kurze Wartezeit

            return True

        except Exception as e:
            print(f"      Fehler: {e}")
            return False

    def cleanup(self):
        self.spi.close()
        # GPIO wird von außen aufgeräumt


def test_all_combinations():
    """Teste alle möglichen Pin-Kombinationen"""

    results = []

    # Alle Permutationen von [17, 24, 25] für [RST, DC, BUSY]
    combinations = list(itertools.permutations(CANDIDATE_PINS))

    print(f"\nTeste {len(combinations)} Kombinationen...\n")

    for i, (rst, dc, busy) in enumerate(combinations, 1):
        print(f"\n[{i}/{len(combinations)}] Teste: RST={rst}, DC={dc}, BUSY={busy}")

        try:
            tester = PinTester(rst, dc, busy)

            # Check BUSY-Verhalten
            busy_before, busy_after = tester.check_busy()
            print(f"   BUSY vor Reset: {busy_before}, nach Reset: {busy_after}")

            # Erwartung: BUSY sollte nach Reset HIGH (1) sein
            busy_ok = (busy_after == 1)

            # Test Clear
            print("   Teste Clear White...")
            clear_ok = tester.test_clear_white()

            tester.cleanup()

            # Bewertung
            score = 0
            if busy_ok:
                score += 10
                print("   ✅ BUSY-Pin verhält sich RICHTIG!")
            if clear_ok:
                score += 5
                print("   ✅ Clear-Befehl OK")

            results.append({
                'rst': rst,
                'dc': dc,
                'busy': busy,
                'busy_before': busy_before,
                'busy_after': busy_after,
                'busy_ok': busy_ok,
                'clear_ok': clear_ok,
                'score': score
            })

            # Cleanup zwischen Tests
            GPIO.cleanup()
            time.sleep(1)

        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            GPIO.cleanup()
            time.sleep(1)

    return results


def print_results(results):
    """Zeige Ergebnisse sortiert nach Score"""
    print("\n" + "="*60)
    print("ERGEBNISSE (sortiert nach Wahrscheinlichkeit)")
    print("="*60)

    # Sortiere nach Score
    results.sort(key=lambda x: x['score'], reverse=True)

    for i, r in enumerate(results, 1):
        print(f"\n{i}. RST={r['rst']}, DC={r['dc']}, BUSY={r['busy']}")
        print(f"   BUSY: vorher={r['busy_before']}, nachher={r['busy_after']}")
        print(f"   Score: {r['score']}/15")

        if r['score'] >= 10:
            print("   ⭐ SEHR WAHRSCHEINLICH RICHTIG!")
        elif r['score'] >= 5:
            print("   ⚠️  Teilweise richtig")
        else:
            print("   ❌ Wahrscheinlich falsch")

    print("\n" + "="*60)

    # Beste Kombination
    best = results[0]
    if best['score'] >= 10:
        print("✅ WAHRSCHEINLICH RICHTIGE KONFIGURATION:")
        print(f"   RST_PIN  = {best['rst']}")
        print(f"   DC_PIN   = {best['dc']}")
        print(f"   BUSY_PIN = {best['busy']}")
        print("\nVERWENDE DIESE PINS in deinem finalen Script!")
    else:
        print("⚠️  KEINE EINDEUTIGE LÖSUNG GEFUNDEN")
        print("Mögliche Ursachen:")
        print("  - Display ist defekt")
        print("  - Pin-Verkabelung ist komplett falsch")
        print("  - BUSY-Pin ist nicht angeschlossen")
        print("\n💡 EMPFEHLUNG:")
        print("  1. Überprüfe die Verkabelung mit einem Multimeter")
        print("  2. Teste mit einem anderen Display")
        print("  3. Ignoriere BUSY-Pin komplett (feste Wartezeiten)")

    print("="*60)


if __name__ == "__main__":
    print("\n⚠️  WICHTIG:")
    print("Dieses Script testet alle Pin-Kombinationen.")
    print("Es dauert ca. 2-3 Minuten.")
    print("\nDrücke ENTER zum Starten, CTRL+C zum Abbrechen...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nAbgebrochen")
        exit(0)

    try:
        results = test_all_combinations()
        print_results(results)

    except KeyboardInterrupt:
        print("\n\nAbgebrochen")
        GPIO.cleanup()

    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        GPIO.cleanup()
