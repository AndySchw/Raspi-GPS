# DIY Outdoor GPS-Gerät

Ein selbstgebautes GPS-Navigationsgerät mit Raspberry Pi Zero 2 W, ähnlich einem Garmin-Geocaching-GPS.

![Status](https://img.shields.io/badge/Status-In%20Entwicklung-yellow)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)

---

## Features

✅ **GPS-Navigation**
- Echtzeit-Position (Latitude, Longitude, Höhe)
- Navigation zu Zielkoordinaten
- Richtungspfeil und Distanz-Anzeige
- Satelliten-Tracking

✅ **Sensoren**
- 9-Achsen IMU (Gyroskop, Beschleunigung, Magnetometer)
- Barometer für präzise Höhenmessung
- Digitaler Kompass mit Kalibrierung
- Schrittzähler

✅ **Display & Bedienung**
- 2.9" ePaper Display (stromsparsam, outdoor-lesbar)
- Menü-Navigation per Drehencoder
- Energiesparende Updates

✅ **Track-Logging**
- Automatische Aufzeichnung von Routen
- GPX-Export für Google Earth, Komoot, etc.
- Statistiken (Distanz, Höhenmeter, Schritte)

✅ **Webinterface**
- WLAN-Hotspot auf dem Pi
- Track-Download über Browser
- Geräte-Konfiguration

---

## Hardware

### Hauptkomponenten
- **Raspberry Pi Zero 2 W** (1 GHz Quad-Core, 512 MB RAM)
- **2.9" ePaper Display** (296×128 Pixel, SPI)
- **u-blox NEO-M8N GPS** mit Antenne (UART)
- **MPU-9250** IMU (I²C)
- **BMP180** Barometer (I²C)
- **Drehencoder** (KY-040)
- **Piezo-Buzzer**
- **Powerbank** 10000-20000 mAh

**Kosten:** ca. 80-130€

Vollständige Einkaufsliste: [`docs/hardware/shopping-list.md`](docs/hardware/shopping-list.md)

---

## Installation

### 1. Hardware zusammenbauen

Verkabelung siehe: [`docs/hardware/pinout.md`](docs/hardware/pinout.md)

**Wichtig:**
- GPS-Modul OBEN im Gehäuse platzieren
- Alle Sensoren mit 3.3V betreiben (kein 5V!)
- Raspberry Pi beim Verkabeln ausschalten

### 2. Raspberry Pi einrichten

```bash
# Raspberry Pi OS Lite installieren (via Raspberry Pi Imager)
# SSH aktivieren und einloggen

# Setup-Skript auf Pi kopieren
scp scripts/setup_raspberry_pi.sh pi@raspberrypi.local:~

# Auf Pi einloggen
ssh pi@raspberrypi.local

# Setup ausführen
chmod +x setup_raspberry_pi.sh
sudo ./setup_raspberry_pi.sh

# Reboot (wichtig!)
sudo reboot
```

### 3. Projekt deployen

```bash
# Auf deinem Entwicklungs-PC:
./scripts/deploy.sh
```

Das Skript:
- Überträgt den Code via SSH/rsync
- Installiert Python-Dependencies
- Richtet den Systemd-Service ein

### 4. Programm starten

```bash
# Manuell testen
ssh pi@raspberrypi.local
cd gps_device
venv/bin/python3 src/main.py

# Als Service (startet automatisch beim Boot)
sudo systemctl enable gps-device
sudo systemctl start gps-device

# Logs ansehen
sudo journalctl -u gps-device -f
```

---

## Entwicklung

### Lokale Entwicklung (Mock-Modus)

Entwicklung ist ohne echte Hardware möglich:

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements-dev.txt

# Mock-Modus aktivieren
cp .env.example .env
# In .env: MOCK_MODE=True

# Programm starten
python3 src/main.py
```

Im Mock-Modus werden Hardware-Zugriffe simuliert.

### Tests ausführen

```bash
# Unit-Tests (schnell, ohne Hardware)
pytest -m unit

# Alle Tests
pytest

# Mit Coverage
pytest --cov=src --cov-report=html
```

### Code-Qualität

```bash
# Formatierung
black src/

# Linting
flake8 src/

# Type-Checking
mypy src/
```

---

## Projektstruktur

```
.
├── .claude/                # Claude Code Konfiguration
│   ├── CLAUDE.md          # Projektregeln für Claude
│   ├── agents/            # Spezialisierte Agenten
│   └── commands/          # Slash Commands
├── config/                # Konfigurationsdateien
│   └── default.yaml
├── docs/                  # Dokumentation
│   └── hardware/          # Hardware-Docs
├── hardware/              # Gehäuse-Designs, Schaltpläne
├── scripts/               # Setup & Deployment
├── src/                   # Quellcode
│   ├── gps/              # GPS-Modul
│   ├── imu/              # IMU-Modul
│   ├── navigation/       # Navigationslogik
│   ├── display/          # ePaper Display
│   ├── logging/          # Track-Logging
│   ├── web/              # Webinterface
│   ├── utils/            # Hilfsfunktionen
│   └── main.py           # Hauptprogramm
├── tests/                # Tests
│   ├── unit/
│   ├── integration/
│   ├── hardware/
│   └── mocks/
├── requirements.txt      # Python-Dependencies
└── README.md
```

---

## Claude Code Integration

Dieses Projekt ist optimiert für die Entwicklung mit Claude Code.

### Verfügbare Agenten

Nutze spezialisierte Agenten für komplexe Aufgaben:

- **Hardware-Agent:** Sensor-Integration, GPIO, I²C, SPI
- **Navigation-Agent:** Algorithmen, Koordinaten-Mathematik
- **Display-Agent:** UI-Design, ePaper-Rendering
- **Testing-Agent:** Tests, Mocks, Coverage

### Slash Commands

Schnellzugriff auf häufige Aufgaben:

```bash
/check-project        # Projekt-Status prüfen
/implement-module     # Neues Modul implementieren
/hardware-test        # Hardware testen
/run-tests           # Tests ausführen
/deploy-to-pi        # Auf Pi deployen
```

Mehr in [`.claude/CLAUDE.md`](.claude/CLAUDE.md)

---

## Verwendung

### Menü-Struktur

```
Hauptmenü
├── Navigation        → Ziel setzen, navigieren
├── Track starten     → Aufzeichnung starten
├── Gespeicherte Tracks → Tracks ansehen/exportieren
├── Sensoren          → Live-Sensor-Daten
└── Einstellungen     → Konfiguration
```

### Bedienung

- **Drehencoder drehen:** Menü navigieren
- **Drehencoder drücken:** Auswählen
- **Buzzer:** Feedback bei Aktionen

### Webinterface

```bash
# WLAN-Hotspot aktivieren (auf Pi)
# Dann mit Smartphone/Laptop verbinden zu:
http://gps.local:8080
```

Funktionen:
- Tracks herunterladen (GPX)
- Statistiken ansehen
- Einstellungen ändern

---

## Entwicklungsphasen

### ✅ Phase 1: Projekt-Setup
- [x] Projektstruktur
- [x] Claude Code Integration
- [x] Dokumentation
- [x] Setup-Skripte

### 🔨 Phase 2: Basis-Module (aktuell)
- [ ] GPS-Modul implementieren
- [ ] IMU-Modul implementieren
- [ ] Barometer-Modul implementieren
- [ ] Display-Modul implementieren

### 📋 Phase 3: Navigation
- [ ] Haversine-Distanz
- [ ] Bearing-Berechnung
- [ ] Kompass-Kalibrierung
- [ ] Schrittzähler

### 📋 Phase 4: Logging & Tracking
- [ ] JSON-Logger
- [ ] GPX-Export
- [ ] Statistiken

### 📋 Phase 5: UI & Bedienung
- [ ] Menüsystem
- [ ] Drehencoder-Input
- [ ] Display-Layouts

### 📋 Phase 6: Webinterface
- [ ] Flask-Server
- [ ] Track-Download
- [ ] Konfiguration

---

## Troubleshooting

### GPS bekommt keinen Fix
- GPS-Modul muss oben im Gehäuse sein
- Freie Sicht zum Himmel
- Min. 4 Satelliten nötig (kann 1-2 Minuten dauern)

### I²C-Geräte werden nicht erkannt
```bash
# I²C-Scan durchführen
i2cdetect -y 1

# Sollte zeigen:
# 0x68 = MPU-9250
# 0x77 = BMP180
```

### Display bleibt schwarz
- SPI in `raspi-config` aktiviert?
- Pins korrekt verkabelt?
- Display-Treiber installiert?

### Service startet nicht
```bash
# Logs prüfen
sudo journalctl -u gps-device -n 50

# Service-Status
sudo systemctl status gps-device
```

Mehr in [`docs/hardware/pinout.md`](docs/hardware/pinout.md)

---

## Lizenz

MIT License - siehe LICENSE-Datei

---

## Weitere Ressourcen

- **Hardware-Dokumentation:** [`docs/hardware/`](docs/hardware/)
- **Claude-Agenten:** [`.claude/agents/`](.claude/agents/)
- **Raspberry Pi GPIO:** [pinout.xyz](https://pinout.xyz/)
- **Waveshare ePaper:** [Wiki](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)

---

## Kontakt & Support

Bei Fragen oder Problemen:
- Issue erstellen auf GitHub
- Dokumentation in `docs/` prüfen
- Claude Code mit `/check-project` nutzen

**Viel Erfolg beim Bauen! 🛠️📍**
