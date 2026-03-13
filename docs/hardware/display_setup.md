# Display-Setup: MH-ET LIVE 2.9" ePaper (Rot/Schwarz)

## Hardware-Info

**Modell:** MH-ET LIVE 2.9 inch E-Paper Module
**Controller:** GDEW029Z10
**Auflösung:** 296 x 128 Pixel
**Farben:** Schwarz, Weiß, Rot
**Interface:** SPI (3-line oder 4-line)

**Dokumentation:** AZ-Delivery AZ335
**Datasheet:** `/docs/AZ335_D_08-10_DE_B0B2DQXPVZ.pdf`

---

## Pin-Belegung (Raspberry Pi)

| Display Pin | Raspberry Pi GPIO | Pi Pin-Nummer |
|-------------|-------------------|---------------|
| VCC | 3.3V | Pin 17 |
| GND | GND | Pin 20 |
| SDI (MOSI) | GPIO10 | Pin 19 |
| SCLK | GPIO11 | Pin 23 |
| CS | GPIO8 | Pin 24 |
| D/C | GPIO25 | Pin 22 |
| RST | GPIO24 | Pin 18 |
| BUSY | GPIO17 | Pin 11 |

---

## Software-Setup

### 1. Python-Library installieren

**Auf dem Raspberry Pi:**

```bash
# GxEPD2-ähnliche Library für Python (falls verfügbar)
pip3 install --break-system-packages gxepd2

# Alternativ: Nutze die Arduino GxEPD2-Beispiele als Referenz
```

**WICHTIG:** Die GxEPD2-Library ist primär für Arduino/C++.
Für Python auf dem Raspberry Pi müssen wir einen eigenen Treiber schreiben oder die PIL-basierte Lösung nutzen.

---

### 2. Display-Treiber-Klasse

Siehe: `src/display/epaper_gdew029z10.py`

Die Klasse basiert auf:
- SPI-Kommunikation über `spidev`
- GPIO-Steuerung über `RPi.GPIO`
- Bildverarbeitung mit `PIL`

**Besonderheit:**
- Benötigt **2 separate Bildbuffer**: einen für Schwarz, einen für Rot
- Full Refresh dauert ~2 Sekunden
- Partial Refresh ~0.3 Sekunden (nur für einfache Updates)

---

## Display-Schalter (BS Interface)

Auf der Rückseite des Displays befindet sich ein **BS Interface Schalter**:

- **Position "3"**: 3-line SPI
- **Position "4"**: 4-line SPI (Standard)

**Empfehlung:** Schalter auf **Position "4"** (4-line SPI)

---

## Initialisierungs-Sequenz

```python
import spidev
import RPi.GPIO as GPIO

# Pin-Definitionen
RST_PIN = 24
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 17

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

# SPI Setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000

# Hardware Reset
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.01)
GPIO.output(RST_PIN, GPIO.LOW)
time.sleep(0.01)
GPIO.output(RST_PIN, GPIO.HIGH)
time.sleep(0.01)

# Warte auf BUSY = HIGH (Ready)
while GPIO.input(BUSY_PIN) == 0:
    time.sleep(0.01)
```

---

## Typische Probleme & Lösungen

### Problem: Display bleibt leer

**Ursache:** Falscher Treiber (Waveshare statt GxEPD2)

**Lösung:** Nutze GxEPD2_290_C90c-kompatiblen Code

---

### Problem: BUSY-Pin bleibt auf LOW

**Ursache:** Display hat sich aufgehängt

**Lösung:**
1. Pi ausschalten
2. Display VCC abziehen
3. 30 Sekunden warten
4. VCC wieder anstecken
5. Pi einschalten

---

### Problem: Nur Schwarz funktioniert, kein Rot

**Ursache:** Rot-Buffer wird nicht korrekt gesendet

**Lösung:** Zwei separate Buffer an `display()` übergeben:
```python
display.display(black_buffer, red_buffer)
```

---

## Refresh-Zeiten

- **Full Refresh:** ~2 Sekunden (komplett neu zeichnen)
- **Partial Refresh:** ~0.3 Sekunden (nur Änderungen)
- **Standby Power:** < 0.017mW (extrem stromsparend!)

---

## Code-Beispiel (Arduino-Referenz aus Datenblatt)

```cpp
#include <GxEPD2_3C.h>
#include <Fonts/FreeMonoBold9pt7b.h>

#define EPD_SS 10
#define EPD_DC 9
#define EPD_RST 8
#define EPD_BUSY 7

GxEPD2_3C<GxEPD2_290_C90c, MAX_HEIGHT(GxEPD2_290_C90c)>
    display(GxEPD2_290_C90c(EPD_SS, EPD_DC, EPD_RST, EPD_BUSY));

void setup() {
    display.init(115200);
    display.setRotation(1);
    display.setFont(&FreeMonoBold9pt7b);
    display.setTextColor(GxEPD_BLACK);

    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setCursor(x, y);
        display.print("Hello World!");
    } while (display.nextPage());

    display.hibernate();
}
```

**Für Raspberry Pi:** Diese Logik muss in Python/C++ portiert werden.

---

## Nächste Schritte

1. ✅ Display-Dokumentation aktualisiert
2. ⏳ Python-Treiber für GDEW029Z10 schreiben
3. ⏳ Test-Script mit Rot/Schwarz-Ausgabe
4. ⏳ Integration ins GPS-Projekt

---

## Referenzen

- [GxEPD2 Library (Arduino)](https://github.com/ZinggJM/GxEPD2)
- [AZ-Delivery Produkt-Doku](https://www.az-delivery.de)
- [GDEW029Z10 Datasheet](https://www.good-display.com)
