#!/usr/bin/env python3
"""
Hardware-Check Script für GPS-Gerät

Testet alle angeschlossenen Hardware-Komponenten:
- I²C Bus (MPU-9250, BMP180)
- GPS (UART)
- Display (SPI)
- GPIO (Encoder, Buzzer)
"""

import sys
import time
from pathlib import Path

# Füge src/ zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import smbus2
    import RPi.GPIO as GPIO
    import spidev
    import serial
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("Bitte installiere fehlende Pakete mit:")
    print("  sudo apt install -y python3-smbus2 python3-rpi.gpio python3-spidev python3-serial")
    sys.exit(1)

from src.utils.config import config


class HardwareChecker:
    """Testet alle Hardware-Komponenten"""

    def __init__(self):
        self.results = {}

    def check_i2c(self):
        """Testet I²C Bus und angeschlossene Geräte"""
        print("\n=== I²C Bus Test ===")

        try:
            bus_num = config.get('hardware.pins.i2c.bus', 1)
            bus = smbus2.SMBus(bus_num)

            # Erwartete I²C-Adressen
            expected = {
                0x68: "MPU-9250 (IMU)",
                0x77: "BMP180 (Barometer)"
            }

            found = []
            for addr in range(0x03, 0x78):
                try:
                    bus.read_byte(addr)
                    found.append(addr)
                except:
                    pass

            print(f"Gefundene I²C-Geräte: {len(found)}")

            all_ok = True
            for addr, name in expected.items():
                if addr in found:
                    print(f"  ✅ 0x{addr:02x}: {name}")
                else:
                    print(f"  ❌ 0x{addr:02x}: {name} - NICHT GEFUNDEN!")
                    all_ok = False

            self.results['i2c'] = all_ok
            bus.close()

        except Exception as e:
            print(f"  ❌ I²C-Fehler: {e}")
            self.results['i2c'] = False

    def check_gps(self):
        """Testet GPS-Modul (UART)"""
        print("\n=== GPS (UART) Test ===")

        try:
            port = config.get('hardware.pins.uart.port', '/dev/ttyS0')
            baudrate = config.get('hardware.pins.uart.baudrate', 9600)

            print(f"Öffne {port} mit {baudrate} baud...")
            ser = serial.Serial(port, baudrate, timeout=2)

            # Lies 10 Zeilen
            print("Lese GPS-Daten (5 Sekunden)...")
            nmea_count = 0
            start_time = time.time()

            while time.time() - start_time < 5:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$'):
                    nmea_count += 1
                    if nmea_count <= 3:
                        print(f"  📡 {line[:60]}...")

            ser.close()

            if nmea_count > 0:
                print(f"  ✅ GPS sendet Daten ({nmea_count} NMEA-Sätze empfangen)")
                self.results['gps'] = True
            else:
                print(f"  ⚠️  GPS sendet keine NMEA-Daten")
                self.results['gps'] = False

        except Exception as e:
            print(f"  ❌ GPS-Fehler: {e}")
            self.results['gps'] = False

    def check_spi(self):
        """Testet SPI Bus (Display)"""
        print("\n=== SPI Bus Test ===")

        try:
            bus = config.get('hardware.pins.spi.bus', 0)
            device = config.get('hardware.pins.spi.device', 0)

            spi = spidev.SpiDev()
            spi.open(bus, device)
            spi.max_speed_hz = 2000000

            # Einfacher Schreib-Test
            test_data = [0x00, 0x01, 0x02, 0x03]
            response = spi.xfer2(test_data)

            spi.close()

            print(f"  ✅ SPI Bus {bus}.{device} erreichbar")
            print(f"  📤 Gesendet: {test_data}")
            print(f"  📥 Antwort:  {response}")
            self.results['spi'] = True

        except Exception as e:
            print(f"  ❌ SPI-Fehler: {e}")
            self.results['spi'] = False

    def check_gpio(self):
        """Testet GPIO-Pins (Encoder, Buzzer)"""
        print("\n=== GPIO Test ===")

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Encoder-Pins
            encoder_clk = config.get('hardware.pins.rotary_encoder.clk_gpio', 5)
            encoder_dt = config.get('hardware.pins.rotary_encoder.dt_gpio', 27)
            encoder_sw = config.get('hardware.pins.rotary_encoder.sw_gpio', 6)

            # Buzzer-Pin
            buzzer_pin = config.get('hardware.pins.buzzer.signal_gpio', 22)

            # Display-Pins
            display_dc = config.get('hardware.pins.spi.dc_gpio', 25)
            display_rst = config.get('hardware.pins.spi.rst_gpio', 24)
            display_busy = config.get('hardware.pins.spi.busy_gpio', 17)

            gpio_pins = {
                encoder_clk: "Encoder CLK",
                encoder_dt: "Encoder DT",
                encoder_sw: "Encoder SW",
                buzzer_pin: "Buzzer",
                display_dc: "Display DC",
                display_rst: "Display RST",
                display_busy: "Display BUSY"
            }

            print("Teste GPIO-Pins...")
            all_ok = True

            for pin, name in gpio_pins.items():
                try:
                    # Input-Pins (Encoder, Display BUSY)
                    if 'Encoder' in name or 'BUSY' in name:
                        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                        state = GPIO.input(pin)
                        print(f"  ✅ GPIO{pin:2d} ({name:15s}): Input, State={state}")

                    # Output-Pins (Buzzer, Display)
                    else:
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, GPIO.LOW)
                        print(f"  ✅ GPIO{pin:2d} ({name:15s}): Output")

                except Exception as e:
                    print(f"  ❌ GPIO{pin:2d} ({name:15s}): Fehler - {e}")
                    all_ok = False

            # Buzzer kurz testen (Piep)
            try:
                print("\n  🔊 Teste Buzzer (kurzer Piep)...")
                GPIO.setup(buzzer_pin, GPIO.OUT)
                pwm = GPIO.PWM(buzzer_pin, 2000)  # 2kHz
                pwm.start(50)
                time.sleep(0.2)
                pwm.stop()
                print("  ✅ Buzzer funktioniert!")
            except Exception as e:
                print(f"  ⚠️  Buzzer-Test fehlgeschlagen: {e}")

            GPIO.cleanup()
            self.results['gpio'] = all_ok

        except Exception as e:
            print(f"  ❌ GPIO-Fehler: {e}")
            self.results['gpio'] = False
            GPIO.cleanup()

    def run_all_tests(self):
        """Führt alle Tests aus"""
        print("=" * 60)
        print("GPS-GERÄT HARDWARE-CHECK")
        print("=" * 60)

        self.check_i2c()
        self.check_gps()
        self.check_spi()
        self.check_gpio()

        print("\n" + "=" * 60)
        print("ZUSAMMENFASSUNG")
        print("=" * 60)

        for component, status in self.results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component.upper():10s}: {'OK' if status else 'FEHLER'}")

        all_ok = all(self.results.values())
        print("\n" + "=" * 60)

        if all_ok:
            print("🎉 ALLE HARDWARE-KOMPONENTEN FUNKTIONIEREN!")
            return 0
        else:
            print("⚠️  EINIGE KOMPONENTEN HABEN FEHLER - PRÜFE VERKABELUNG!")
            return 1


def main():
    """Main Entry Point"""
    try:
        checker = HardwareChecker()
        exit_code = checker.run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest abgebrochen.")
        GPIO.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        GPIO.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
