# Hardware-Einkaufsliste

## Benötigte Komponenten

### Hauptkomponenten

| Komponente | Spezifikation | Menge | ca. Preis | Bezugsquelle |
|------------|---------------|-------|-----------|--------------|
| **Raspberry Pi Zero 2 W** | 1 GHz Quad-Core, 512 MB RAM, WLAN, Bluetooth | 1 | 15-20€ | berrybase.de, reichelt.de |
| **MicroSD-Karte** | Min. 16 GB, Class 10, z.B. SanDisk | 1 | 8-12€ | Amazon, Media Markt |
| **2.9" ePaper Display** | 296×128 Pixel, SPI, Waveshare kompatibel | 1 | 15-25€ | Amazon, AliExpress |
| **u-blox NEO-M8N GPS** | Mit Antenne, UART Interface, 3.3V | 1 | 12-20€ | Amazon, AliExpress |
| **MPU-9250** | 9-Achsen IMU (Gyro, Accel, Mag), I²C | 1 | 8-15€ | Amazon, AliExpress |
| **BMP180** | Barometer/Temperatursensor, I²C | 1 | Bereits vorhanden | - |
| **Drehencoder** | Rotary Encoder mit Push-Button (KY-040) | 1 | 2-5€ | Amazon, AliExpress |
| **Piezo-Buzzer** | Passiv, 3-5V, z.B. KY-006 | 1 | 1-3€ | Amazon, AliExpress |
| **Powerbank** | 10000-20000 mAh, USB-C, min. 2A Output | 1 | 15-30€ | Amazon, Media Markt |

**Gesamtpreis Hauptkomponenten:** ca. **80-130€**

---

### Verkabelung & Verbindungen

| Komponente | Spezifikation | Menge | ca. Preis |
|------------|---------------|-------|-----------|
| **Dupont-Kabel Set** | Female-Female, 20 cm, verschiedene Farben | 1 Set (40 Stk) | 5-8€ |
| **Breadboard** | 400 oder 830 Kontakte (optional für Tests) | 1 | 3-5€ |
| **GPIO Header** | 2×20 Pin (falls Pi ohne Header) | 1 | 2-3€ |
| **Lötzinn** | Bleifreies Lötzinn (falls Löten nötig) | 1 Rolle | 5-10€ |

**Optional aber empfohlen:**
- **Lötkolben** (falls noch nicht vorhanden): 15-30€
- **Multimeter** für Fehlersuche: 10-20€

---

### Gehäuse & Mechanik

| Komponente | Spezifikation | Menge | ca. Preis | Hinweis |
|------------|---------------|-------|-----------|---------|
| **PLA/PETG Filament** | Für 3D-Druck, ca. 100g benötigt | 1 Rolle | 0€ | Du hast bereits einen 3D-Drucker |
| **M2.5 Schrauben** | 6-10 mm Länge, für Pi-Befestigung | 4-8 Stk | 2-5€ | Schrauben-Set |
| **M3 Schrauben** | Für Gehäuse-Montage | 8-12 Stk | 2-5€ | Schrauben-Set |
| **Acrylglas** | 2-3 mm dick, für Display-Abdeckung | 1 Stück | 3-8€ | Baumarkt zuschneiden lassen |
| **Gummidichtung** | Optional, für Outdoor-Schutz | 1 m | 3-5€ | Baumarkt |

---

### Optional: Erweiterungen

| Komponente | Zweck | ca. Preis |
|------------|-------|-----------|
| **DHT11** | Temperatur/Luftfeuchte-Sensor | 2-5€ |
| **LED** | Status-Anzeige (rot, grün, blau) | 1-3€ |
| **Schalter** | Ein/Aus-Schalter | 1-3€ |
| **LiPo Akku 3.7V** | Für kompaktere Bauweise statt Powerbank | 10-20€ |
| **LiPo-Lademodul** | TP4056 mit Schutzschaltung | 2-5€ |
| **Step-Up-Converter** | 3.7V → 5V für Pi (bei LiPo-Nutzung) | 3-8€ |

---

## Spezifikationen im Detail

### Raspberry Pi Zero 2 W
- **Prozessor:** Broadcom BCM2710A1, 1 GHz Quad-Core ARM Cortex-A53
- **RAM:** 512 MB LPDDR2
- **WLAN:** 2.4 GHz 802.11 b/g/n
- **Bluetooth:** 4.2, BLE
- **GPIO:** 40 Pins
- **Stromverbrauch:** ~150-300 mA (idle), ~500 mA (Last)
- **USB:** Micro-USB (Daten), USB-C (Power - nur bei neueren Versionen)

**Hinweis:** Falls USB-C Power nicht verfügbar, Micro-USB mit Adapter nutzen.

---

### 2.9" ePaper Display
**Empfehlung:** Waveshare 2.9" ePaper oder kompatibel

- **Auflösung:** 296×128 Pixel
- **Farben:** Schwarz/Weiß (keine Graustufen)
- **Interface:** SPI (4-Wire)
- **Refresh:** 2s (Full), 0.3s (Partial)
- **Stromverbrauch:** <4 mA (aktiv), 0 µA (Sleep)
- **Spannung:** 3.3V
- **Größe:** ~80×36 mm (sichtbare Fläche)

**Wichtig:** Achte auf SPI-Interface (nicht I²C)!

**Produkt-Links (Beispiele):**
- Waveshare 2.9inch E-Ink Display Module (Amazon ~20€)
- GeeekPi 2.9" ePaper HAT (Amazon ~18€)

---

### u-blox NEO-M8N GPS
**Empfehlung:** Modul mit integrierter Antenne

- **Chipsatz:** u-blox NEO-M8N
- **Kanäle:** 72
- **Genauigkeit:** 2.5 m (ohne DGPS)
- **Update-Rate:** 1-10 Hz (Standard: 1 Hz)
- **Kaltstart:** ~26s
- **Warmstart:** ~1s
- **Interface:** UART (9600 baud)
- **Protokoll:** NMEA 0183, UBX
- **Spannung:** 3.3-5V (meist 3.3V empfohlen)
- **Stromverbrauch:** ~50 mA

**Wichtig:** Mit Antenne kaufen (Keramik-Patch oder externe Antenne)!

**Produkt-Links (Beispiele):**
- Beitian BN-880 GPS Module mit Kompass (~15€)
- GY-NEO6MV2 (alternative, etwas günstiger aber älterer Chip ~10€)

---

### MPU-9250
**9-Achsen IMU (Inertial Measurement Unit)**

- **Gyroskop:** 3-Achsen, ±250/500/1000/2000 °/s
- **Beschleunigung:** 3-Achsen, ±2/4/8/16 g
- **Magnetometer:** 3-Achsen (AK8963)
- **Interface:** I²C oder SPI (meist I²C)
- **I²C-Adresse:** 0x68 (Standard) oder 0x69
- **Spannung:** 3.3V
- **Stromverbrauch:** ~3.5 mA

**Alternative:** MPU-6050 (ohne Magnetometer, nur 6-Achsen) ~5€

**Produkt-Links:**
- GY-9250 Breakout Board (Amazon/AliExpress ~10€)

---

### KY-040 Drehencoder
**Rotary Encoder mit Druckschalter**

- **Impulse:** 20-30 pro Umdrehung
- **Spannung:** 3.3-5V
- **Ausgänge:** CLK, DT, SW, VCC, GND
- **Besonderheit:** Mechanisch, mit Rastung

**Produkt-Links:**
- KY-040 Drehencoder Set (Amazon 5 Stück ~8€)

---

### Powerbank
**Andy's Setup:**
- **Kapazität:** 10000 mAh ✅
- **Output:** USB-C, bis 15W ✅
- **Wichtig:** Muss **Niedrigstrom-Modus** unterstützen!

Viele Powerbanks schalten bei geringem Stromverbrauch (<100mA) ab.

**Stromverbrauch GPS-Gerät:**
- Idle: ~200 mA (1W)
- Aktiv (GPS, Display): ~400-600 mA (2-3W)
- Durchschnitt: ~400 mA (2W)

**Laufzeit-Rechnung mit 10000 mAh:**
```
Theorie: 10000 mAh / 400 mA = 25 Stunden
Real: ~12-15 Stunden (Verluste durch DC-DC Wandlung ~20%)

Bei sparsamem Modus (Display alle 5s):
→ ~15-18 Stunden möglich
```

**Tipp:** Bei längeren Touren (>12h) zweite Powerbank mitnehmen oder Solar-Ladegerät.

---

## Bezugsquellen

### Deutschland
- **berrybase.de** - Raspberry Pi Spezialist
- **reichelt.de** - Elektronik-Versand
- **conrad.de** - Elektronik & Technik
- **Amazon.de** - Schneller Versand, breite Auswahl

### International (länger Lieferzeit, günstiger)
- **AliExpress** - Sehr günstig, 2-4 Wochen Lieferzeit
- **Banggood** - Ähnlich wie AliExpress

### Lokal
- **Conrad Filiale** - Sofort verfügbar, etwas teurer
- **Baumarkt** - Schrauben, Acrylglas

---

## Budget-Varianten

### Minimal-Setup (~60€)
- Raspberry Pi Zero 2 W
- GPS-Modul (günstigeres GY-NEO6MV2)
- MPU-6050 (statt MPU-9250, ohne Magnetometer)
- Kleines OLED statt ePaper (~5€)
- Vorhandene Powerbank nutzen
- Breadboard statt Gehäuse

### Standard-Setup (~100€)
- Wie oben in der Hauptliste

### Premium-Setup (~150€)
- Zusätzlich: LiPo-Akku mit Lademodul
- Wasserdichtes Gehäuse (fertig gekauft)
- Externe GPS-Antenne für besseren Empfang
- Größeres ePaper Display (4.2")

---

## Werkzeug (falls noch nicht vorhanden)

| Werkzeug | Zweck | ca. Preis |
|----------|-------|-----------|
| **Lötkolben Set** | Für Breadboard-Alternative | 20-40€ |
| **Abisolierzange** | Kabel abisolieren | 10-15€ |
| **Multimeter** | Fehlersuche, Spannungsmessung | 15-30€ |
| **Micro-USB Kabel** | Pi mit Powerbank verbinden | 3-8€ |
| **SD-Karten-Adapter** | Pi OS installieren | 3-5€ |
| **Pinzette** | Kleinteile handhaben | 5-10€ |

---

## Checkliste vor Bestellung

- [ ] Raspberry Pi Zero 2 W (nicht Zero 1, zu langsam!)
- [ ] MicroSD-Karte (min. 16 GB)
- [ ] ePaper Display mit **SPI** Interface
- [ ] GPS-Modul **mit Antenne**
- [ ] MPU-9250 oder MPU-6050
- [ ] BMP180 bereits vorhanden ✓
- [ ] Drehencoder (KY-040)
- [ ] Buzzer (passiv, 3-5V)
- [ ] Dupont-Kabel (Female-Female)
- [ ] Powerbank (mit Niedrigstrom-Modus)
- [ ] Optional: Breadboard für Tests

**Gesamt-Budget:** ca. **80-130€** (je nach Bezugsquelle)

---

## Lieferzeiten einplanen

- **Deutschland/EU:** 2-5 Tage
- **China (AliExpress):** 2-4 Wochen
- **Raspberry Pi:** Oft Lieferengpässe, vorher Verfügbarkeit prüfen!

**Tipp:** Pi Zero 2 W kann schwer verfügbar sein. Alternative: Raspberry Pi 4A (~10€ teurer, gleiche Funktionalität).
