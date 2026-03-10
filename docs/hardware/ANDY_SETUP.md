# Andy's Hardware-Setup

Dokumentation der tatsächlich verwendeten Komponenten.

---

## 🎯 Komplette Hardware-Liste

### Zentrale Komponenten

| Komponente | Modell/Details | Status | Notizen |
|------------|----------------|--------|---------|
| **Raspberry Pi** | Zero 2 W | ✅ Vorhanden | 1GHz Quad-Core, 512MB RAM |
| **SD-Karte** | 64GB SanDisk Extreme Pro | ✅ Vorhanden | A2, sehr schnell, zuverlässig |
| **Powerbank** | 10000 mAh, USB-C, 15W | ✅ Vorhanden | Laufzeit: 12-15h |

### Sensoren & Module

| Komponente | Modell/Details | Status | Notizen |
|------------|----------------|--------|---------|
| **GPS** | u-blox NEO-M8N | 🛒 Bestellt | Multi-GNSS, externe Antenne |
| **Display** | 2.9" ePaper 296×128 | 🛒 Bestellt | SPI, Schwarz/Weiß |
| **IMU** | MPU-9250 | 🛒 Bestellt | 9-Achsen (Gyro/Accel/Mag) |
| **Barometer** | BMP180 | ✅ Vorhanden | I²C, 0x77 |

### Eingabe & Feedback

| Komponente | Modell/Details | Status | Notizen |
|------------|----------------|--------|---------|
| **Encoder** | KY-040 Rotary Encoder | ✅ Vorhanden | CLK/DT/SW |
| **Buzzer** | Piezo Buzzer | ✅ Vorhanden | Passiv, PWM-gesteuert |

### Sonstiges

| Komponente | Details | Status | Zweck |
|------------|---------|--------|-------|
| **USB-LAN Adapter** | USB → Ethernet | ✅ Vorhanden | Setup, Debugging (optional) |
| **Dupont-Kabel** | Female-Female | ? | Verkabelung |

---

## 📡 GPS: u-blox NEO-M8N

### Spezifikationen
- **Chipsatz:** u-blox NEO-M8N (moderne Version)
- **GNSS:** GPS + GLONASS + Galileo + BeiDou
- **Genauigkeit:** 2-3 Meter (horizontal)
- **Update-Rate:** 1-10 Hz (Standard: 1 Hz)
- **Interface:** UART
- **Baudrate:** 9600 bps (Standard)
- **Antenne:** Externe Patch-Antenne (flexibel positionierbar)
- **Kaltstart:** ~26 Sekunden
- **Warmstart:** ~1 Sekunde
- **Stromverbrauch:** ~50 mA

### Vorteile
✅ **Multi-GNSS** → besserer Empfang, mehr Satelliten
✅ **Externe Antenne** → optimal im Gehäuse positionierbar
✅ **NEO-M8N** → moderner als NEO-6M, bessere Genauigkeit
✅ **UART** → einfache Integration, kein USB nötig

### Anschluss
```
GPS          Raspberry Pi
VCC    →     Pin 1  (3.3V)
GND    →     Pin 6  (GND)
TX     →     Pin 10 (GPIO15 RXD)
RX     →     Pin 8  (GPIO14 TXD)
```

**WICHTIG:** NEO-M8N läuft mit **3.3V** (nicht 5V!)

---

## 🎛️ Steuerung: KY-040 Rotary Encoder

### Funktionen
- **Drehen:** Menü hoch/runter navigieren
- **Drücken:** Auswahl bestätigen
- **CLK + DT:** Drehrichtung erkennen
- **SW:** Button-Input

### Anschluss
```
Encoder      Raspberry Pi
CLK    →     Pin 11 (GPIO17)
DT     →     Pin 13 (GPIO27)
SW     →     Pin 15 (GPIO22)
+      →     Pin 17 (3.3V)
GND    →     Pin 14 (GND)
```

### Software-Handling
```python
# Interrupt-basiert (effizient)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.BOTH, callback=encoder_callback)
```

---

## 🔋 Stromversorgung: 10000 mAh Powerbank

### Spezifikationen
- **Kapazität:** 10000 mAh (37 Wh bei 3.7V)
- **Output:** USB-C, bis 15W
- **Input:** USB-C (Laden)

### Stromverbrauch GPS-Gerät

| Modus | Verbrauch | Beschreibung |
|-------|-----------|--------------|
| **Idle** | ~200 mA (1W) | Display schläft, GPS minimal |
| **Aktiv** | ~400-600 mA (2-3W) | GPS + Display + Sensoren |
| **Peak** | ~800 mA (4W) | Display Full-Refresh + alle Sensoren |

**Durchschnitt:** ~400 mA (2W)

### Laufzeit-Kalkulation

```
Powerbank: 10000 mAh @ 5V = 50 Wh
Pi braucht: 5V @ 400mA = 2W

Theorie: 50 Wh / 2W = 25 Stunden

Praktisch:
- DC-DC Wandlung: ~80% Effizienz
- Powerbank Alterung: ~90%
- Temperaturschwankungen: ~95%

Real: 25h × 0.8 × 0.9 × 0.95 = ~17 Stunden

Konservativ: 12-15 Stunden
```

### Energie-Optimierung

**Für längere Laufzeit:**
```yaml
# config/default.yaml
display:
  update_interval: 5.0  # statt 2.0 Sekunden

power:
  display_sleep_after: 120  # nach 2 Min Inaktivität
  gps_sleep_if_no_movement: true
```

**Mögliche Laufzeit mit Optimierung:** 15-18 Stunden

---

## 💾 Speicher: 64GB SanDisk Extreme Pro

### Spezifikationen
- **Kapazität:** 64 GB
- **Geschwindigkeit:** bis 170 MB/s lesen, 90 MB/s schreiben
- **Rating:** A2 (optimiert für Apps/Random I/O)
- **Klasse:** UHS-I, U3, V30

### Vorteile für GPS-Gerät
✅ **Sehr schnell** → kein Logging-Bottleneck
✅ **A2-Rating** → perfekt für Raspberry Pi OS
✅ **Zuverlässig** → weniger Datenverlust
✅ **64GB** → Platz für tausende Tracks

### Speicherplatz-Kalkulation

**GPS-Track (1 Stunde):**
```
JSON: ~5 KB pro Minute = 300 KB/h
GPX:  ~10 KB pro Minute = 600 KB/h
```

**Bei 64 GB:**
```
JSON: 64 GB / 300 KB = ~213.000 Stunden = ~24 Jahre
GPX:  64 GB / 600 KB = ~106.000 Stunden = ~12 Jahre
```

**Praktisch:** Speicher reicht für **mehrere tausend Touren** 🎉

### Logging-Strategie

**Standard:**
- JSON-Logs: Alle 5 Sekunden
- GPX-Export: Bei Track-Ende

**High-Detail Mode (mit 64GB möglich):**
```yaml
tracking:
  log_interval: 1.0  # Jede Sekunde!
  high_detail: true
```

→ Noch immer Platz für tausende Touren

---

## 🔌 USB-LAN Adapter (optional)

### Zweck
- **Initiales Setup:** Wenn WLAN nicht funktioniert
- **Debugging:** Stabile Verbindung für SSH
- **Updates:** Schneller als WLAN

### Verwendung
```bash
# Pi mit Ethernet verbinden
# IP-Adresse finden:
ip addr show eth0

# SSH via Ethernet:
ssh pi@<ethernet-ip>
```

**Im fertigen Gerät:** Nicht nötig, nur für Entwicklung/Setup nützlich

---

## 📊 Hardware-Status

### ✅ Vorhanden (5/9)
- Raspberry Pi Zero 2 W
- 64GB SD-Karte
- BMP180 Barometer
- KY-040 Encoder
- Piezo Buzzer
- 10000 mAh Powerbank
- USB-LAN Adapter

### 🛒 Bestellt (3/9)
- GPS NEO-M8N
- 2.9" ePaper Display
- MPU-9250 IMU

### ⏳ Optional (1/9)
- Dupont-Kabel (falls nicht vorhanden)

**Bereit:** ████████████████░░ 89%

---

## 🎯 Besonderheiten deines Setups

### 1. Multi-GNSS GPS
**Vorteil gegenüber Standard-GPS:**
- Mehr Satelliten verfügbar (GPS+GLONASS+Galileo+BeiDou)
- Besserer Empfang in schwierigem Gelände (Wald, Stadt)
- Schnellerer Fix
- Genauere Position

### 2. SanDisk Extreme Pro SD
**Vorteil gegenüber Standard-SD:**
- 3-5x schneller → flüssigeres System
- A2-Rating → besseres App-Performance
- Zuverlässiger → weniger Datenverlust
- Ermöglicht hochfrequentes Logging (1 Hz statt 5 Hz)

### 3. 10000 mAh Powerbank
**Optimal für Tagestouren:**
- 12-15 Stunden Laufzeit
- Kompakt und leicht
- USB-C für moderne Geräte

---

## ⚡ Power-Management Empfehlungen

### Standard-Modus (12-15h)
```yaml
display:
  update_interval: 2.0
power:
  low_power_mode: false
```

### Langstrecken-Modus (15-18h)
```yaml
display:
  update_interval: 5.0
  full_refresh_every: 20  # weniger Full-Refreshs
power:
  low_power_mode: true
  display_sleep_after: 120
  gps_sleep_if_no_movement: true
```

### Ultra-Spar-Modus (20h+)
```yaml
display:
  update_interval: 10.0
tracking:
  log_interval: 10.0  # statt 5s
power:
  low_power_mode: true
```

---

## 📝 Nächste Schritte

### Wenn GPS + Display ankommen:

1. **Verkabeln** nach `pinout.md`
2. **Hardware testen:**
   ```bash
   i2cdetect -y 1  # Sollte 0x68 + 0x77 zeigen
   cgps -s         # GPS-Test
   ```
3. **Mir SSH-Zugang geben**
4. **Software installieren & Module implementieren**

---

**Hardware-Setup Stand:** 2024-03-09
**Vollständigkeit:** 89% (nur noch 3 Teile ausstehend)
