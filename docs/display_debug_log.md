# Display-Debugging Log - GDEW029Z10

**Datum:** 15. März 2026
**Display:** MH-ET LIVE 2.9" ePaper (GDEW029Z10) - Rot/Schwarz/Weiß
**Status:** Teilweise funktionierend, aber nicht vollständig kontrollierbar

---

## Hardware-Verkabelung

### Aktuelle Verkabelung:
```
Display → Raspberry Pi Zero 2 W
VCC    → 3.3V (Pin 17)
GND    → GND (Pin 20)
SDI    → GPIO10 (Pin 19) - MOSI
SCLK   → GPIO11 (Pin 23)
CS     → GPIO8 (Pin 24) - CE0
D/C    → GPIO25 (Pin 22)
RST    → GPIO24 (Pin 18)  ⚠️ MÖGLICHERWEISE FALSCH!
BUSY   → GPIO17 (Pin 11)  ⚠️ MÖGLICHERWEISE FALSCH!
```

### Pin-Reihenfolge am Display (von unten nach oben):
```
VCC, GND, SDI, SCLK, CS, D/C, RST, BUSY
```

### ⚠️ WICHTIGSTER VERDACHT:
**RST und BUSY könnten VERTAUSCHT sein!**

**Nächster Test:** Tausche GPIO24 (RST) und GPIO17 (BUSY) und teste nochmal!

```python
# AKTUELL:
RST_PIN = 24   # ← Vielleicht falsch!
BUSY_PIN = 17  # ← Vielleicht falsch!

# ZUM TESTEN:
RST_PIN = 17   # ← Tauschen!
BUSY_PIN = 24  # ← Tauschen!
```

---

## Was funktioniert hat

### ✅ SPI-Kommunikation
- Display reagiert auf SPI-Befehle
- Flackert bei Updates
- Zeigt manchmal Farben (rot, weiß)

### ✅ Richtige Befehle identifiziert
- **Schwarz-Buffer:** 0x24
- **Rot-Buffer:** 0x26
- **Update:** 0x20
- **CS-Pin:** Wird von spidev automatisch gesteuert (NICHT manuell!)

### ✅ Richtige Auflösung identifiziert
- **296x128 Pixel** (Querformat!)
- **Nicht** 128x296!

### ✅ RAM-Adressierung
- **X:** 0x00 bis 0x24 (37 bytes = 296 pixel / 8)
- **Y:** 0x00 bis 0x7F (128 Zeilen)

---

## Was NICHT funktioniert

### ❌ Schwarz-Buffer wird oft ignoriert
- Nur Rot-Buffer zeigt manchmal Reaktion
- Schwarz wird nicht angezeigt
- Hintergrund bleibt oft rot

### ❌ BUSY-Pin verhält sich komisch
- Zeigt immer 0 (LOW) im Idle-Zustand
- Sollte normalerweise 1 (HIGH) sein wenn idle
- **Verdacht:** RST und BUSY sind vertauscht!

### ❌ Display zeigt keine kontrollierbaren Bilder
- Nur Pixel-Chaos, rote Flächen, weiße Rechtecke
- Kein sauberer Text oder klare Grafiken
- **Grund:** Wahrscheinlich falsche Pin-Zuordnung!

---

## Korrekte Init-Sequenz (gefunden)

```python
def init(self):
    self.reset()

    self.cmd(0x12)  # SWRESET
    time.sleep(0.3)

    self.cmd(0x01)  # Driver Output Control
    self.data([0x27, 0x01, 0x00])  # 296 Zeilen

    self.cmd(0x11)  # Data Entry Mode
    self.data(0x03)  # Y inc, X inc

    self.cmd(0x44)  # RAM X-Adresse
    self.data([0x00, 0x24])  # 0 bis 0x24 (37 bytes)

    self.cmd(0x45)  # RAM Y-Adresse
    self.data([0x00, 0x00, 0x7F, 0x00])  # 0 bis 127

    self.cmd(0x3C)  # Border
    self.data(0x05)

    self.cmd(0x18)  # Temperature
    self.data(0x80)

    self.cmd(0x4E)  # X Counter
    self.data(0x00)

    self.cmd(0x4F)  # Y Counter
    self.data([0x00, 0x00])
```

---

## Test-Scripts

### Wichtigste funktionierende Scripts:
1. **`scripts/test_display_fixed.py`**
   - Alle Fehler behoben (außer Pin-Zuordnung)
   - Auflösung 296x128
   - CS automatisch
   - ABER: RST/BUSY evtl. falsch!

2. **`scripts/test_display_alive.py`**
   - Zeigt dass Display grundsätzlich reagiert
   - Flackern sichtbar

---

## Nächste Schritte (beim nächsten Mal)

### 1. RST und BUSY tauschen! ⚠️ WICHTIGSTER SCHRITT!

**Test-Script mit getauschten Pins:**

```python
#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO

# GETAUSCHT!
RST_PIN = 17   # War vorher 24
BUSY_PIN = 24  # War vorher 17
DC_PIN = 25

EPD_WIDTH = 296
EPD_HEIGHT = 128

class TestSwapped:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(BUSY_PIN, GPIO.IN)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0

    def cmd(self, c):
        GPIO.output(DC_PIN, 0)
        self.spi.xfer2([c])

    def data(self, d):
        GPIO.output(DC_PIN, 1)
        if isinstance(d, int):
            d = [d]
        self.spi.xfer2(d)

    def wait_busy(self):
        print(f"BUSY vor Wait: {GPIO.input(BUSY_PIN)}")
        timeout = 0
        while GPIO.input(BUSY_PIN) == 0:
            time.sleep(0.01)
            timeout += 1
            if timeout > 2000:
                print("TIMEOUT!")
                return
        print(f"BUSY nach Wait: {GPIO.input(BUSY_PIN)}")

    def reset(self):
        GPIO.output(RST_PIN, 0)
        time.sleep(0.2)
        GPIO.output(RST_PIN, 1)
        time.sleep(0.5)

    def test_clear(self):
        print("Test: Clear White mit GETAUSCHTEN Pins!")
        self.reset()
        self.wait_busy()

        self.cmd(0x12)
        time.sleep(0.3)
        self.wait_busy()

        self.cmd(0x01)
        self.data([0x27, 0x01, 0x00])

        self.cmd(0x11)
        self.data(0x03)

        self.cmd(0x44)
        self.data([0x00, 0x24])

        self.cmd(0x45)
        self.data([0x00, 0x00, 0x7F, 0x00])

        self.cmd(0x3C)
        self.data(0x05)

        self.cmd(0x18)
        self.data(0x80)

        self.cmd(0x4E)
        self.data(0x00)

        self.cmd(0x4F)
        self.data([0x00, 0x00])

        self.wait_busy()

        # Clear white
        bytes_total = int(EPD_WIDTH * EPD_HEIGHT / 8)

        self.cmd(0x24)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x26)
        for i in range(bytes_total):
            self.data(0xFF)

        self.cmd(0x20)
        print("Warte 10 Sekunden...")
        time.sleep(10)
        print("Sollte WEISS sein!")

try:
    epd = TestSwapped()
    epd.test_clear()
    GPIO.cleanup()
except:
    GPIO.cleanup()
    raise
```

**Speichern als:** `scripts/test_swapped_pins.py`

**Ausführen:**
```bash
cd ~/gps_device
sudo python3 scripts/test_swapped_pins.py
```

---

### 2. Wenn das funktioniert:

Dann **ALLE anderen Pins auch nochmal prüfen**:
- Multimeter verwenden
- Pin-Beschriftung am Display genau ablesen
- Vergleichen mit tatsächlicher Verkabelung

---

### 3. Wenn das NICHT funktioniert:

**Alternative Displays testen:**
- Waveshare 2.9" Original
- Anderer Hersteller mit garantierter Raspberry Pi Kompatibilität

---

## Wichtige Erkenntnisse

### 1. CS-Pin NICHT manuell steuern
```python
# FALSCH:
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.output(CS_PIN, 0)
self.spi.xfer2([data])
GPIO.output(CS_PIN, 1)

# RICHTIG:
# Kein GPIO.setup für CS!
self.spi.xfer2([data])  # spidev steuert CE0 automatisch
```

### 2. Auflösung ist 296x128 (Querformat)
```python
# FALSCH:
EPD_WIDTH = 128
EPD_HEIGHT = 296

# RICHTIG:
EPD_WIDTH = 296
EPD_HEIGHT = 128
```

### 3. RAM-Fenster muss zur Auflösung passen
```python
# FALSCH:
self.data([0x00, 0x0F])  # Nur 128 pixel breit

# RICHTIG:
self.data([0x00, 0x24])  # 296 pixel breit (37 bytes)
```

### 4. PIL.tobytes() kann Probleme machen
- Bytes nicht immer in richtiger Reihenfolge
- Eventuell manuelle Byte-Konvertierung nötig
- **Aber:** Erst wenn Hardware richtig funktioniert!

---

## Referenzen

### Befehls-Übersicht:
- **0x01:** Driver Output Control (Zeilen-Anzahl)
- **0x11:** Data Entry Mode (Scan-Richtung)
- **0x12:** Software Reset
- **0x18:** Temperature Sensor Control
- **0x20:** Display Update (Master Activation)
- **0x24:** Write RAM (Black/White)
- **0x26:** Write RAM (Red)
- **0x3C:** Border Waveform Control
- **0x44:** Set RAM X Address Start/End
- **0x45:** Set RAM Y Address Start/End
- **0x4E:** Set RAM X Address Counter
- **0x4F:** Set RAM Y Address Counter

### Buffer-Logik:
- **Schwarz-Buffer (0x24):** 0x00 = schwarz, 0xFF = weiß
- **Rot-Buffer (0x26):** 0x00 = rot, 0xFF = transparent (zeigt Schwarz-Buffer)
- **Beide 0xFF:** Weiß
- **0x24=0x00, 0x26=0xFF:** Schwarz
- **0x24=0xFF, 0x26=0x00:** Rot

---

## Hardware-Info

**Display:** MH-ET LIVE 2.9" ePaper Module
**Controller:** IL0373 / UC8151
**Auflösung:** 296x128 Pixel
**Farben:** Schwarz, Weiß, Rot
**Interface:** SPI (4-wire)
**BS Interface Schalter:** Muss auf Position "4" stehen!

---

## TODO beim nächsten Mal

- [ ] RST und BUSY Pins tauschen (GPIO24 ↔ GPIO17)
- [ ] Test mit getauschten Pins durchführen
- [ ] BUSY-Verhalten beobachten (sollte HIGH sein wenn idle)
- [ ] Wenn erfolgreich: Finalen Display-Treiber schreiben
- [ ] Wenn nicht erfolgreich: Alternatives Display bestellen

---

**Erstellt:** 15. März 2026
**Letzter Stand:** Display reagiert auf SPI, aber zeigt keine kontrollierbaren Bilder
**Nächster Schritt:** RST/BUSY Pins tauschen!
