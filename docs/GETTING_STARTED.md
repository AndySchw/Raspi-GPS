# Getting Started - Schritt-für-Schritt Anleitung

Diese Anleitung führt dich vom Auspacken der Komponenten bis zum ersten funktionierenden GPS-Gerät.

---

## Überblick

Der Aufbau erfolgt in diesen Phasen:

1. **Hardware beschaffen** (1-2 Wochen Lieferzeit)
2. **Raspberry Pi vorbereiten** (30 Minuten)
3. **Komponenten verkabeln** (1-2 Stunden)
4. **Software installieren** (30 Minuten)
5. **Hardware testen** (30 Minuten)
6. **Erste Inbetriebnahme** (15 Minuten)

**Gesamt-Zeit:** ca. 3-4 Stunden (ohne Lieferzeit)

---

## Phase 1: Hardware beschaffen

### Einkaufsliste prüfen

Siehe detaillierte Liste: [`hardware/shopping-list.md`](../hardware/shopping-list.md)

**Mindest-Setup (~80€):**
- [ ] Raspberry Pi Zero 2 W
- [ ] MicroSD-Karte 16GB+
- [ ] 2.9" ePaper Display (SPI)
- [ ] GPS NEO-M8N mit Antenne
- [ ] MPU-9250 IMU
- [ ] BMP180 Barometer
- [ ] Drehencoder KY-040
- [ ] Buzzer
- [ ] Dupont-Kabel (Female-Female)
- [ ] Powerbank 10000mAh+

### Bezugsquellen

**Schnell (Deutschland):**
- berrybase.de (Raspberry Pi)
- Amazon.de (restliche Komponenten)

**Günstig (China):**
- AliExpress (2-4 Wochen Lieferzeit)

---

## Phase 2: Raspberry Pi vorbereiten

### Schritt 1: Raspberry Pi OS installieren

**Benötigt:** PC/Mac mit SD-Karten-Leser

1. **Raspberry Pi Imager** herunterladen: [rpiimager.com](https://www.raspberrypi.com/software/)

2. **OS auswählen:**
   - Operating System → Raspberry Pi OS (other) → **Raspberry Pi OS Lite (64-bit)**
   - Keine Desktop-Umgebung nötig, spart Strom

3. **Einstellungen (Zahnrad-Icon):**
   - Hostname: `raspberrypi`
   - SSH aktivieren: ✅ (mit Passwort)
   - Username: `pi`
   - Passwort: (dein sicheres Passwort)
   - WLAN konfigurieren: SSID + Passwort eingeben
   - Locale: Deutschland, Timezone: Europe/Berlin

4. **Schreiben:**
   - MicroSD-Karte auswählen
   - "Schreiben" klicken
   - Warten (~5 Minuten)

5. **SD-Karte in Pi einlegen** und Pi mit Strom versorgen

### Schritt 2: Erste Verbindung

**Warte 1-2 Minuten** bis Pi gebootet ist.

```bash
# SSH-Verbindung testen
ssh pi@raspberrypi.local

# Passwort eingeben
```

Falls `raspberrypi.local` nicht funktioniert:
```bash
# IP-Adresse im Router finden oder:
ping raspberrypi.local
```

**Erfolgreich?** ✅ Weiter zu Phase 3

**Probleme?**
- Pi leuchtet nicht → Strom prüfen
- Verbindung timeout → WLAN-Daten prüfen
- Hostname nicht gefunden → IP-Adresse direkt nutzen

---

## Phase 3: Komponenten verkabeln

**⚠️ WICHTIG: Raspberry Pi AUSSCHALTEN vor dem Verkabeln!**

```bash
# Auf dem Pi:
sudo shutdown -h now
```

### Schritt 1: Verkabelungs-Plan

Öffne: [`hardware/pinout.md`](../hardware/pinout.md)

Dort findest du:
- Genaue Pin-Nummern
- Schaltplan
- Verkabelungs-Checkliste

### Schritt 2: Breadboard-Aufbau (empfohlen für Tests)

**Reihenfolge:**

1. **Breadboard vorbereiten**
   - Power-Rails verbinden: 3.3V und GND vom Pi

2. **GPS-Modul (NEO-M8N)**
   ```
   GPS VCC  → Pi Pin 1  (3.3V)
   GPS GND  → Pi Pin 6  (GND)
   GPS TX   → Pi Pin 10 (GPIO15/RXD)
   GPS RX   → Pi Pin 8  (GPIO14/TXD)
   ```

3. **I²C-Bus (MPU-9250 + BMP180)**
   ```
   Beide Module parallel an I²C:
   SDA → Pi Pin 3  (GPIO2)
   SCL → Pi Pin 5  (GPIO3)
   VCC → 3.3V
   GND → GND
   ```

4. **ePaper Display**
   ```
   VCC  → Pi Pin 17 (3.3V)
   GND  → Pi Pin 20 (GND)
   DIN  → Pi Pin 19 (GPIO10/MOSI)
   CLK  → Pi Pin 23 (GPIO11/SCLK)
   CS   → Pi Pin 24 (GPIO8)
   DC   → Pi Pin 22 (GPIO25)
   RST  → Pi Pin 18 (GPIO24)
   BUSY → Pi Pin 11 (GPIO17) [optional]
   ```

5. **Drehencoder**
   ```
   CLK → Pi Pin 11 (GPIO17)
   DT  → Pi Pin 13 (GPIO27)
   SW  → Pi Pin 15 (GPIO22)
   +   → 3.3V
   GND → GND
   ```

6. **Buzzer**
   ```
   Signal → Pi Pin 15 (GPIO22)
   GND    → GND
   ```

### Schritt 3: Verkabelung prüfen

**Visuell checken:**
- [ ] Keine losen Kabel
- [ ] Keine Kurzschlüsse zwischen 3.3V und GND
- [ ] Alle Module haben VCC und GND
- [ ] Richtige GPIO-Pins verwendet

**Multimeter (falls vorhanden):**
- Durchgangsprüfung für GND-Verbindungen
- 3.3V zwischen VCC und GND messen (Pi einschalten)

### Schritt 4: GPS-Antenne positionieren

⚠️ **SEHR WICHTIG für GPS-Empfang:**

- GPS-Modul OBEN platzieren
- Freie Sicht nach oben
- Weg von Metall-Objekten
- Nicht unter anderen Komponenten

---

## Phase 4: Software installieren

### Schritt 1: Setup-Skript ausführen

```bash
# Auf deinem PC/Mac:
# Setup-Skript auf Pi kopieren
scp scripts/setup_raspberry_pi.sh pi@raspberrypi.local:~

# Auf Pi einloggen
ssh pi@raspberrypi.local

# Setup ausführen
chmod +x setup_raspberry_pi.sh
sudo ./setup_raspberry_pi.sh
```

Das Skript:
- Aktualisiert System
- Installiert Python 3 + Dependencies
- Aktiviert I²C, SPI, UART
- Installiert GPS-Daemon
- Installiert Waveshare ePaper Library
- Erstellt Systemd Service

**Dauer:** ~10-15 Minuten

### Schritt 2: Reboot

```bash
sudo reboot
```

**Wichtig:** Reboot aktiviert die Interface-Einstellungen (I²C, SPI, UART)

### Schritt 3: Projekt-Code deployen

```bash
# Auf deinem PC/Mac:
./scripts/deploy.sh
```

Falls du Git nutzt:
```bash
git init
git add .
git commit -m "Initial commit"

# Dann deploy.sh ausführen
./scripts/deploy.sh
```

---

## Phase 5: Hardware testen

### Test 1: I²C-Bus

```bash
ssh pi@raspberrypi.local
i2cdetect -y 1
```

**Erwartete Ausgabe:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
...
60: -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77
```

- `0x68` = MPU-9250 ✅
- `0x77` = BMP180 ✅

**Problem:** Keine Geräte gefunden
→ Verkabelung prüfen (SDA/SCL)
→ I²C in raspi-config aktiviert?

### Test 2: GPS

```bash
# GPS-Daemon Status
sudo systemctl status gpsd

# GPS-Daten live ansehen
cgps -s
```

**Erwartete Ausgabe nach 1-2 Minuten:**
```
┌───────────────────────────────────────────┐
│    Time:       2024-03-09T12:34:56.000Z  │
│    Latitude:    52.520008               │
│    Longitude:    13.404954              │
│    Altitude:   34.0 m                   │
│    Satellites: 8                        │
└───────────────────────────────────────────┘
```

**Problem:** Keine Satelliten
→ GPS-Modul nach draußen oder ans Fenster
→ Kann 2-10 Minuten dauern beim Kaltstart

### Test 3: SPI (Display)

```bash
ls /dev/spidev*
```

**Erwartete Ausgabe:**
```
/dev/spidev0.0  /dev/spidev0.1
```

✅ SPI funktioniert

### Test 4: GPIO (Drehencoder)

```bash
cd ~/gps_device
venv/bin/python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
```

**Erwartete Ausgabe:**
```
GPIO OK
```

---

## Phase 6: Erste Inbetriebnahme

### Programm im Test-Modus starten

```bash
ssh pi@raspberrypi.local
cd ~/gps_device

# Aktiviere Virtual Environment
source venv/bin/activate

# Starte Hauptprogramm
python3 src/main.py
```

**Erwartete Ausgabe:**
```
2024-03-09 12:34:56 - main - INFO - === GPS-Gerät gestartet ===
2024-03-09 12:34:56 - main - INFO - Mock-Modus: False
2024-03-09 12:34:57 - main - INFO - Initialisiere Hardware-Module...
2024-03-09 12:34:58 - main - INFO - Alle Hardware-Module erfolgreich initialisiert
2024-03-09 12:34:58 - main - INFO - Starte Haupt-Loop...
```

### Testen

**Drehencoder:**
- Drehen → sollte im Log erscheinen
- Drücken → sollte Aktion auslösen

**Display:**
- Sollte GPS-Daten anzeigen
- Updates alle 2 Sekunden

**GPS:**
- Warte auf Fix (1-10 Minuten)
- Koordinaten sollten erscheinen

### Beenden

```
Strg+C
```

**Erwartete Ausgabe:**
```
2024-03-09 12:45:30 - main - INFO - Programm durch Benutzer beendet
2024-03-09 12:45:30 - main - INFO - Räume auf...
2024-03-09 12:45:30 - main - INFO - Cleanup abgeschlossen
2024-03-09 12:45:30 - main - INFO - === GPS-Gerät beendet ===
```

---

## Service einrichten (optional)

Automatischer Start beim Boot:

```bash
# Service aktivieren
sudo systemctl enable gps-device

# Service starten
sudo systemctl start gps-device

# Status prüfen
sudo systemctl status gps-device

# Logs live ansehen
sudo journalctl -u gps-device -f
```

---

## Nächste Schritte

### Entwicklung fortsetzen

1. **Module implementieren:**
   ```bash
   # In Claude Code:
   /implement-module GPS
   /implement-module IMU
   /implement-module Navigation
   ```

2. **Tests schreiben:**
   ```bash
   /run-tests
   ```

3. **Gehäuse designen:**
   - Mit Fusion 360 / FreeCAD
   - Für 3D-Druck vorbereiten
   - GPS OBEN platzieren!

### Häufige Probleme

**Problem:** GPS findet keine Satelliten
- **Lösung:** Nach draußen, min. 5 Minuten warten, GPS-Antenne oben

**Problem:** Display bleibt schwarz
- **Lösung:** SPI-Pins prüfen, Treiber neu installieren

**Problem:** I²C-Geräte nicht gefunden
- **Lösung:** Verkabelung prüfen, i2cdetect ausführen

**Problem:** Programm startet nicht
- **Lösung:** Logs prüfen: `sudo journalctl -u gps-device -n 50`

---

## Ressourcen

- **Hardware-Pinout:** [`hardware/pinout.md`](../hardware/pinout.md)
- **Einkaufsliste:** [`hardware/shopping-list.md`](../hardware/shopping-list.md)
- **Projekt-README:** [`../README.md`](../README.md)
- **Claude-Agenten:** [`../.claude/agents/`](../.claude/agents/)

---

## Support

Bei Problemen:
1. Logs prüfen: `sudo journalctl -u gps-device -f`
2. Hardware-Tests durchführen (Phase 5)
3. Dokumentation checken
4. Issue auf GitHub erstellen

**Viel Erfolg! 🚀**
