# DIY Outdoor GPS Gerät - Claude Projektregeln

## Projekt Übersicht
Ein selbstgebautes GPS-Navigationsgerät mit Raspberry Pi Zero 2 W, ähnlich einem Garmin-Geocaching-GPS.

**Hauptfunktionen:**
- GPS-Navigation mit Richtungspfeil und Distanz
- Höhenmesser und Schrittzähler
- Track-Logging auf SD-Karte
- ePaper Display für stromsparendes Outdoor-Display
- WLAN-Webinterface zum Daten-Download
- Bedienung per Drehencoder

---

## Hardware-Komponenten

### Kern
- **Raspberry Pi Zero 2 W** (Hauptsteuerung)
- **2.9" ePaper Display** (SPI)
- **Drehencoder** (GPIO)
- **Buzzer** (GPIO)
- **Powerbank** (Stromversorgung)

### Sensoren
- **u-blox NEO-M8N** GPS-Modul (UART)
- **MPU-9250** IMU - Gyroskop, Beschleunigung, Magnetometer (I²C)
- **BMP180** Barometer für Höhenmessung (I²C)
- **DHT11** Temperatur/Luftfeuchte - optional (GPIO)

### Anschlüsse
```
GPIO-Layout Raspberry Pi Zero 2 W:
- UART (GPIO14/15): GPS NEO-M8N
- I²C (GPIO2/3): MPU-9250, BMP180
- SPI (GPIO10/11/8/7): ePaper Display
- GPIO17/27: Drehencoder
- GPIO22: Buzzer
- GPIO4: DHT11 (optional)
```

---

## Software-Architektur

### Technologie-Stack
- **Sprache:** Python 3.11+
- **GPS:** gpsd + gpsd-py3
- **Display:** Waveshare ePaper Library
- **IMU:** smbus2 + eigene Treiber
- **Webserver:** Flask (leichtgewichtig)
- **Logging:** JSON + GPX-Export

### Module-Struktur
```
src/
├── gps/          # GPS-Modul (NEO-M8N Interface)
├── imu/          # IMU-Modul (MPU-9250, Kompass, Schrittzähler)
├── navigation/   # Navigationslogik (Haversine, Richtung)
├── display/      # ePaper Display-Rendering
├── logging/      # Track-Logging (JSON, GPX)
├── web/          # Flask Webinterface
└── utils/        # Hilfsfunktionen
```

---

## Code-Regeln für dieses Projekt

### Allgemein
- **Sprache:** Deutsch für Kommentare, deutsche Variablennamen wo sinnvoll
- **Fehlerbehandlung:** Immer explizit, besonders bei Hardware-Zugriff
- **Logging:** Strukturiert mit Zeitstempel, niemals sensible GPS-Daten in öffentliche Logs

### Hardware-Zugriff
- Jeder Hardware-Zugriff muss in try/except mit spezifischem Error-Handling
- Bei I²C/SPI-Fehlern: 3 Retry-Versuche mit exponential backoff
- GPIO-Cleanup in finally-Blöcken
- Sensor-Initialisierung mit Timeout (max 10s)

### Energieoptimierung
- Display nur alle 2-5 Sekunden aktualisieren
- GPS-Abfrage auf 1 Hz reduzieren wenn keine Bewegung
- Sleep-Modus zwischen Updates
- Keine polling-loops, immer Event-basiert oder mit sleep()

### Navigation
- Haversine-Formel für Distanzberechnung
- Bearing-Berechnung für Richtungspfeil
- Kompass-Kalibrierung beim Start verpflichtend
- Höhenmeter aus Barometer, GPS nur als Backup

### Datenformate
- **Track-Logs:** JSON (für Echtzeit) + GPX (für Export)
- **Konfiguration:** YAML-Dateien in config/
- **Keine Secrets:** Alle WLAN-Credentials in .env

---

## Agenten-System

### Verfügbare Agenten

#### 1. Hardware-Integration Agent
**Zuständig für:**
- Sensor-Treiber implementieren
- GPIO/I²C/SPI/UART-Kommunikation
- Hardware-Tests schreiben
- Pin-Belegung validieren

**Aufruf:** `/hardware-agent <Beschreibung>`

#### 2. Navigation-Algorithmus Agent
**Zuständig für:**
- Haversine-Formel implementieren
- Bearing-Berechnung
- Distanz- und Richtungslogik
- Koordinaten-Mathematik

**Aufruf:** `/nav-agent <Beschreibung>`

#### 3. Display-Rendering Agent
**Zuständig für:**
- ePaper-Layouts entwerfen
- Menüstruktur implementieren
- Energiesparende Updates
- Icon-Rendering (Pfeile, Symbole)

**Aufruf:** `/display-agent <Beschreibung>`

#### 4. Testing Agent
**Zuständig für:**
- Unit-Tests für alle Module
- Hardware-Mock-Tests
- Integration-Tests
- Test-Coverage sicherstellen

**Aufruf:** `/test-agent <Beschreibung>`

---

## Entwicklungs-Phasen

### Phase 1: Hardware-Setup ✓
- [ ] Raspberry Pi OS Lite installieren
- [ ] Alle Sensoren anschließen
- [ ] Pin-Belegung testen
- [ ] GPS-Empfang verifizieren

### Phase 2: Basis-Module
- [ ] GPS-Modul (Koordinaten auslesen)
- [ ] IMU-Modul (Kompass, Beschleunigung)
- [ ] Barometer (Höhe, Luftdruck)
- [ ] Display (Text-Rendering)

### Phase 3: Navigation
- [ ] Distanz-Berechnung
- [ ] Richtungspfeil
- [ ] Zielverwaltung
- [ ] Kompass-Kalibrierung

### Phase 4: Logging & Tracking
- [ ] JSON-Logger
- [ ] GPX-Export
- [ ] Schrittzähler
- [ ] SD-Karten-Management

### Phase 5: UI & Bedienung
- [ ] Menüsystem
- [ ] Drehencoder-Input
- [ ] Display-Layouts
- [ ] Buzzer-Feedback

### Phase 6: Webinterface
- [ ] Flask-Server
- [ ] Track-Download
- [ ] Statistiken
- [ ] WLAN-Hotspot

---

## Wichtige Befehle

### Entwicklung
```bash
# Projekt auf Raspberry Pi kopieren
scp -r . pi@raspberrypi.local:~/gps_device/

# SSH-Verbindung
ssh pi@raspberrypi.local

# Hauptprogramm starten
python3 src/main.py

# Tests ausführen
pytest tests/
```

### Hardware-Tests
```bash
# GPS-Test
python3 tests/test_gps.py

# Display-Test
python3 tests/test_display.py

# Alle Sensoren testen
python3 scripts/hardware_check.py
```

---

## Typische Probleme & Lösungen

### GPS kein Fix
- **Ursache:** GPS-Modul nicht oben im Gehäuse
- **Lösung:** Freie Sicht zum Himmel, min. 4 Satelliten

### I²C-Fehler
- **Ursache:** Falsche Pull-Up-Widerstände oder Adresskonflikte
- **Lösung:** `i2cdetect -y 1` ausführen, Adressen prüfen

### Display bleibt schwarz
- **Ursache:** SPI nicht aktiviert oder falsche Pins
- **Lösung:** `sudo raspi-config` → Interface Options → SPI enable

### Kompass zeigt falsche Richtung
- **Ursache:** Magnetometer nicht kalibriert
- **Lösung:** Kalibrierungs-Routine beim Start durchführen

### Hoher Stromverbrauch
- **Ursache:** Display zu häufig aktualisiert
- **Lösung:** Update-Rate auf 2-5 Sekunden reduzieren

---

## Sicherheit & Best Practices

### DSGVO-Konformität
- GPS-Tracks sind personenbezogene Daten
- Keine automatische Cloud-Synchronisation
- User muss Tracks manuell exportieren
- Logs älter als 30 Tage automatisch löschen (optional)

### Stromversorgung
- Nie GPIO-Pins direkt mit 5V verbinden
- Immer über Level-Shifter bei 5V-Sensoren
- Powerbank mit min. 2A Output
- Überspannungsschutz empfohlen

### Gehäuse-Design
- GPS-Antenne OBEN im Gehäuse
- Belüftung für Raspberry Pi
- Display hinter klarem Acrylglas
- Wasserdichte Dichtungen für Outdoor-Nutzung

---

## Nützliche Links

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [u-blox NEO-M8N Datasheet](https://www.u-blox.com/en/product/neo-m8-series)
- [MPU-9250 Register Map](https://invensense.tdk.com/products/motion-tracking/9-axis/mpu-9250/)
- [Waveshare ePaper Wiki](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
- [GPX Format Specification](https://www.topografix.com/gpx.asp)

---

## Claude-spezifische Hinweise

### Beim Coden beachten
- Hardware-Module immer mit Mock-Modus für Tests ohne echte Hardware
- Alle Sensor-Klassen mit `enable_mock=True` Parameter
- Configs aus YAML laden, nie hardcoded
- Type Hints verwenden (Python 3.11+)

### Bei Änderungen
- Immer zuerst Hardware-Dokumentation prüfen
- Pin-Belegung in docs/hardware/pinout.md aktualisieren
- Tests aktualisieren wenn API sich ändert
- CHANGELOG.md pflegen

### Performance-Kritische Bereiche
- Display-Rendering (nur bei Änderungen neu zeichnen)
- GPS-Parsing (gpsd macht das bereits effizient)
- Track-Logging (Batch-Writes alle 10 Sekunden)
- Kompass-Berechnungen (Caching von 500ms)
