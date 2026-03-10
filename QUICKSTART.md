# Quick Start - GPS-Gerät

## Was ist das Projekt?

Ein **DIY Outdoor GPS-Gerät** mit Raspberry Pi Zero 2 W - ähnlich einem Garmin-Geocaching-GPS.

**Features:**
- GPS-Navigation mit Richtungspfeil
- Höhenmesser & Schrittzähler
- Track-Logging & GPX-Export
- ePaper Display (outdoor-lesbar)
- Webinterface für Track-Download

**Kosten:** ~80-130€ | **Zeit:** 3-4 Stunden Aufbau

---

## Schnellübersicht

### 1. Hardware kaufen
📄 [`docs/hardware/shopping-list.md`](docs/hardware/shopping-list.md)

**Hauptkomponenten:**
- Raspberry Pi Zero 2 W
- 2.9" ePaper Display
- GPS NEO-M8N
- MPU-9250 IMU
- Powerbank

### 2. Raspberry Pi vorbereiten
```bash
# Raspberry Pi OS Lite flashen (via Raspberry Pi Imager)
# SSH aktivieren, WLAN konfigurieren
```

### 3. Hardware verkabeln
📄 [`docs/hardware/pinout.md`](docs/hardware/pinout.md)

⚠️ **Wichtig:** GPS-Modul OBEN platzieren!

### 4. Software installieren
```bash
# Setup-Skript auf Pi kopieren
scp scripts/setup_raspberry_pi.sh pi@raspberrypi.local:~

# Auf Pi ausführen
ssh pi@raspberrypi.local
chmod +x setup_raspberry_pi.sh
sudo ./setup_raspberry_pi.sh
sudo reboot

# Projekt deployen
./scripts/deploy.sh
```

### 5. Hardware testen
```bash
ssh pi@raspberrypi.local

# I²C-Bus (sollte 0x68 und 0x77 zeigen)
i2cdetect -y 1

# GPS (warte auf Satelliten)
cgps -s

# SPI
ls /dev/spidev*
```

### 6. Programm starten
```bash
cd ~/gps_device
venv/bin/python3 src/main.py
```

---

## Claude Code nutzen

### Verfügbare Agenten
- **Hardware-Agent:** Sensor-Integration
- **Navigation-Agent:** Algorithmen, Koordinaten
- **Display-Agent:** UI-Design, ePaper
- **Testing-Agent:** Tests, Mocks

### Slash Commands
```bash
/check-project      # Status prüfen
/implement-module   # Modul implementieren
/hardware-test      # Hardware testen
/run-tests         # Tests ausführen
/deploy-to-pi      # Deployment
```

### Module implementieren
```bash
/implement-module GPS         # GPS-Modul
/implement-module IMU         # IMU-Sensor
/implement-module Navigation  # Navigationslogik
/implement-module Display     # ePaper Display
```

---

## Projektstruktur

```
GPS/
├── .claude/           # Claude Code Konfiguration
│   ├── CLAUDE.md     # Projektregeln
│   ├── agents/       # 4 Agenten
│   └── commands/     # 5 Slash Commands
├── docs/             # Dokumentation
├── scripts/          # Setup & Deploy
├── src/              # Quellcode
│   ├── gps/         # GPS-Modul
│   ├── imu/         # IMU-Modul
│   ├── navigation/  # Navigation
│   ├── display/     # Display
│   └── main.py      # Hauptprogramm
└── tests/           # Tests
```

---

## Entwicklungsphasen

**Status:** Setup ✅ | Entwicklung 🔨

- [x] **Phase 1:** Projekt-Setup (100%)
- [ ] **Phase 2:** Basis-Module (0%)
- [ ] **Phase 3:** Navigation (0%)
- [ ] **Phase 4:** UI/Display (0%)
- [ ] **Phase 5:** Webinterface (0%)
- [ ] **Phase 6:** Gehäuse (0%)

---

## Wichtige Dateien

| Datei | Beschreibung |
|-------|-------------|
| [`README.md`](README.md) | Projekt-Übersicht |
| [`GETTING_STARTED.md`](docs/GETTING_STARTED.md) | Detaillierte Anleitung |
| [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | Aktueller Status |
| [`.claude/CLAUDE.md`](.claude/CLAUDE.md) | Claude-Regeln |
| [`hardware/pinout.md`](docs/hardware/pinout.md) | GPIO-Belegung |
| [`hardware/shopping-list.md`](docs/hardware/shopping-list.md) | Einkaufsliste |

---

## Nächste Schritte

### Hardware noch nicht da?
1. Einkaufsliste checken
2. Komponenten bestellen
3. Mock-Entwicklung starten:
   ```bash
   # In config/default.yaml:
   hardware.enable_mock: true
   ```

### Hardware vorhanden?
1. Setup-Skript ausführen
2. Hardware verkabeln
3. Module implementieren:
   ```bash
   /implement-module GPS
   ```

---

## Troubleshooting

**GPS findet keine Satelliten**
→ GPS-Modul nach oben, 5-10 Min warten

**I²C-Geräte nicht gefunden**
→ `i2cdetect -y 1` ausführen, Verkabelung prüfen

**Display bleibt schwarz**
→ SPI aktiviert? Pins korrekt?

**Service startet nicht**
→ `sudo journalctl -u gps-device -n 50`

---

## Support

- **Dokumentation:** [`docs/`](docs/)
- **Claude Hilfe:** `/check-project` ausführen
- **Hardware-Docs:** [`docs/hardware/`](docs/hardware/)

---

**Viel Erfolg beim Bauen! 🛠️📍**
