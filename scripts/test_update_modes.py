#!/usr/bin/env python3
"""
TESTE VERSCHIEDENE UPDATE-MODI

Problem: Während des Flackerns ist das RICHTIGE Bild sichtbar,
         aber am Ende wird es wieder ÜBERSCHRIEBEN!

Mögliche Lösung:
- Unterschiedliche Update-Befehle verwenden
- Partial Refresh statt Full Refresh
- Display nach Update in "Hold"-Modus setzen
"""

import time
import spidev
import RPi.GPIO as GPIO

RST_PIN = 24
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

print("="*60)
print("TESTE VERSCHIEDENE UPDATE-MODI")
print("="*60)

class UpdateModeTester:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.01)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.01)

    def init(self):
        """Standard Init"""
        self.reset()
        time.sleep(0.2)

        self.cmd(0x12)  # SW Reset
        time.sleep(0.5)

        self.cmd(0x01)  # Driver Output
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)  # Data Entry Mode
        self.data(0x03)

        self.cmd(0x44)  # RAM X
        self.data([0x00, 0x24])

        self.cmd(0x45)  # RAM Y
        self.data([0x00, 0x00, 0x7F, 0x00])

        self.cmd(0x3C)  # Border
        self.data(0x05)

        self.cmd(0x18)  # Temp
        self.data(0x80)

        self.cmd(0x4E)  # X Counter
        self.data(0x00)

        self.cmd(0x4F)  # Y Counter
        self.data([0x00, 0x00])

        time.sleep(0.2)

    def draw_big_black_box(self):
        """Zeichne EINE GROSSE schwarze Box"""
        print("   Zeichne GROSSE schwarze Box...")
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        # Black Buffer: Große Box in der Mitte
        self.cmd(0x24)
        for y in range(128):
            for x_byte in range(37):
                # Box: Y 20-108, X-Byte 5-32
                if 20 <= y < 108 and 5 <= x_byte < 32:
                    self.data(0x00)  # Schwarz
                else:
                    self.data(0xFF)  # Weiß

        # Red Buffer: Transparent
        self.cmd(0x26)
        for _ in range(bytes_total):
            self.data(0xFF)

    def update_mode_1_standard(self):
        """Standard Update mit 0x20"""
        print("   UPDATE MODE 1: Standard (0x20)")
        self.cmd(0x20)
        print("   Warte 5 Sekunden...")
        time.sleep(5)

    def update_mode_2_with_sequences(self):
        """Update mit Display Update Sequence 1 und 2"""
        print("   UPDATE MODE 2: Mit Display Update Sequences")

        # Display Update Control 1
        self.cmd(0x21)
        self.data(0x00)  # Normal mode

        # Display Update Control 2 (Master Activation)
        self.cmd(0x20)

        print("   Warte 5 Sekunden...")
        time.sleep(5)

    def update_mode_3_with_control(self):
        """Update mit Display Update Control 2"""
        print("   UPDATE MODE 3: Mit Update Control 2")

        # Display Update Control 2
        self.cmd(0x22)
        self.data(0xC7)  # Enable Clock, Enable Analog, Display Pattern, Disable Analog, Disable OSC

        # Master Activation
        self.cmd(0x20)

        print("   Warte 5 Sekunden...")
        time.sleep(5)

    def update_mode_4_minimal(self):
        """Minimaler Update - nur 0x20, kein Wait"""
        print("   UPDATE MODE 4: Minimal (0x20 ohne lange Wartezeit)")
        self.cmd(0x20)
        print("   Warte nur 1 Sekunde...")
        time.sleep(1)

    def update_mode_5_with_deep_sleep_disable(self):
        """Update und dann sofort Deep Sleep VERHINDERN"""
        print("   UPDATE MODE 5: Update + Deep Sleep DISABLE")

        self.cmd(0x22)
        self.data(0xC7)  # Full update sequence

        self.cmd(0x20)  # Master Activation

        print("   Warte 5 Sekunden...")
        time.sleep(5)

        # WICHTIG: KEIN Deep Sleep! Display aktiv lassen!
        print("   >>> KEIN Deep Sleep - Display bleibt aktiv! <<<")

    def update_mode_6_partial_refresh(self):
        """Partial Refresh Mode"""
        print("   UPDATE MODE 6: Partial Refresh")

        # Display Update Control 2 (Partial Update)
        self.cmd(0x22)
        self.data(0xCF)  # Partial update sequence

        self.cmd(0x20)

        print("   Warte 5 Sekunden...")
        time.sleep(5)


if __name__ == "__main__":
    print("\n⚠️  Dieser Test probiert 6 verschiedene Update-Modi")
    print("\nACHTUNG: Schau während des FLACKERNS genau hin!")
    print("Wenn du die schwarze Box während des Flackerns siehst,")
    print("dann notiere dir bei welchem Modus sie auch NACH dem")
    print("Flackern noch da ist!")
    print("="*60)

    try:
        tester = UpdateModeTester()

        modes = [
            ("Standard (0x20)", tester.update_mode_1_standard),
            ("Mit Sequences", tester.update_mode_2_with_sequences),
            ("Mit Control 2", tester.update_mode_3_with_control),
            ("Minimal", tester.update_mode_4_minimal),
            ("Deep Sleep Disable", tester.update_mode_5_with_deep_sleep_disable),
            ("Partial Refresh", tester.update_mode_6_partial_refresh)
        ]

        for i, (name, update_func) in enumerate(modes, 1):
            print(f"\n\n{'='*60}")
            print(f"TEST {i}/6: {name}")
            print(f"{'='*60}")

            tester.init()
            tester.draw_big_black_box()
            update_func()

            print("\n>>> ENDERGEBNIS <<<")
            print("Siehst du die große SCHWARZE BOX?")
            print("Oder ist wieder das alte Bild da?")

            if i < len(modes):
                input("\nENTER für nächsten Modus...")

        print("\n" + "="*60)
        print("WELCHER MODUS HAT DIE BOX BEHALTEN?")
        print("="*60)
        print("Wenn KEINER: Dann ist das ein Hardware/Firmware-Problem")
        print("Wenn EINER: NOTIERE DIR DIE NUMMER!")
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
