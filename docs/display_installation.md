# Display-Installation auf Raspberry Pi

## Schritt-für-Schritt Anleitung für MH-ET LIVE 2.9" Display

---

## Befehle für den Raspberry Pi

### 1. System-Pakete installieren

```bash
# SPI und GPIO-Tools
sudo apt update
sudo apt install -y python3-spidev python3-rpi.gpio python3-pil

# Optional: Debugging-Tools
sudo apt install -y spi-tools
```

---

### 2. Python-Dependencies installieren

```bash
# Bildverarbeitung
pip3 install --break-system-packages Pillow

# GPIO (sollte schon installiert sein)
pip3 install --break-system-packages RPi.GPIO

# SPI (sollte schon installiert sein)
pip3 install --break-system-packages spidev
```

---

### 3. Display-Test ausführen

```bash
cd ~/gps_device

# Projekt aktualisieren
git pull

# Display-Test (nachdem wir den Treiber geschrieben haben)
sudo python3 scripts/test_mhet_display.py
```

---

## Verkabelung prüfen

**Vor dem Test nochmal checken:**

```bash
# SPI-Devices anzeigen
ls -l /dev/spidev*
# Sollte zeigen: /dev/spidev0.0 und /dev/spidev0.1

# GPIO-Status prüfen
gpio readall  # Falls gpio-tools installiert
```

---

## Display-Pins (Zur Erinnerung)

```
Display  →  Raspberry Pi
VCC      →  3.3V (Pin 17)
GND      →  GND (Pin 20)
SDI      →  GPIO10 (Pin 19) - MOSI
SCLK     →  GPIO11 (Pin 23)
CS       →  GPIO8 (Pin 24)
D/C      →  GPIO25 (Pin 22)
RST      →  GPIO24 (Pin 18)
BUSY     →  GPIO17 (Pin 11)
```

---

## Troubleshooting

### Display reagiert nicht

```bash
# 1. Hardware-Reset
sudo shutdown now
# Dann: VCC abziehen, 30 Sek warten, VCC anstecken, Pi starten

# 2. SPI-Test
sudo python3 -c "import spidev; spi=spidev.SpiDev(); spi.open(0,0); print('SPI OK')"

# 3. GPIO-Test
sudo python3 scripts/test_display_debug.py
```

---

### BS Interface Schalter

Der Schalter auf der Display-Rückseite **MUSS auf Position "4"** stehen (4-line SPI).

Falls auf Position "3":
1. Pi ausschalten
2. Schalter auf "4" stellen
3. Pi einschalten

---

## Nächste Schritte

Nach erfolgreicher Installation:

1. Test mit einfachem Schwarz/Weiß-Bild
2. Test mit Rot/Schwarz/Weiß-Bild
3. Integration ins GPS-Projekt
