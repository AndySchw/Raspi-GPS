# GPIO Pin-Belegung Raspberry Pi Zero 2 W

## Übersicht

```
Raspberry Pi Zero 2 W GPIO Header (40 Pins)

     3.3V  (1) (2)  5V
GPIO2/SDA  (3) (4)  5V
GPIO3/SCL  (5) (6)  GND
    GPIO4  (7) (8)  GPIO14/TXD
      GND  (9) (10) GPIO15/RXD
   GPIO17 (11) (12) GPIO18
   GPIO27 (13) (14) GND
   GPIO22 (15) (16) GPIO23
     3.3V (17) (18) GPIO24
GPIO10/MOSI(19)(20) GND
 GPIO9/MISO(21)(22) GPIO25
GPIO11/SCLK(23)(24) GPIO8/CE0
      GND (25) (26) GPIO7/CE1
   GPIO0  (27) (28) GPIO1
   GPIO5  (29) (30) GND
   GPIO6  (31) (32) GPIO12
  GPIO13  (33) (34) GND
  GPIO19  (35) (36) GPIO16
  GPIO26  (37) (38) GPIO20
      GND (39) (40) GPIO21
```

## Belegte Pins für GPS-Gerät

### I²C Bus (MPU-9250, BMP180)
- **GPIO2** (Pin 3) → SDA (I²C Data)
- **GPIO3** (Pin 5) → SCL (I²C Clock)

**Adressen:**
- MPU-9250: `0x68` (IMU)
- BMP180: `0x77` (Barometer)

**Pull-Up Widerstände:** 4.7kΩ auf SDA und SCL (meist schon auf Modulen vorhanden)

---

### UART (GPS NEO-M8N)
- **GPIO14** (Pin 8) → TXD (Transmit) → RX am GPS
- **GPIO15** (Pin 10) → RXD (Receive) → TX am GPS
- **GND** (Pin 6 oder 9) → GND am GPS
- **3.3V** (Pin 1) → VCC am GPS

**Baudrate:** 9600 bps (Standard für NEO-M8N)

**WICHTIG:** NEO-M8N läuft mit 3.3V - KEIN 5V!

---

### SPI (2.9" ePaper Display)
- **GPIO10** (Pin 19) → MOSI/DIN (Master Out Slave In)
- **GPIO11** (Pin 23) → SCLK/CLK (Clock)
- **GPIO8** (Pin 24) → CE0/CS (Chip Select)
- **GPIO25** (Pin 22) → DC (Data/Command)
- **GPIO24** (Pin 18) → RST (Reset)
- **GPIO17** (Pin 11) → BUSY (optional, für Status)

**Stromversorgung Display:**
- **3.3V** (Pin 17) → VCC
- **GND** (Pin 20) → GND

---

### GPIO (Drehencoder)
- **GPIO5** (Pin 29) → CLK (Clock/A)
- **GPIO27** (Pin 13) → DT (Data/B)
- **GPIO6** (Pin 31) → SW (Switch/Button) mit Pull-Up
- **GND** (Pin 14) → GND

**Hinweis:** Drehencoder nutzt interne Pull-Up-Widerstände des Pi.

---

### GPIO (Buzzer)
- **GPIO22** (Pin 15) → Buzzer Signal
- **GND** (Pin 20) → Buzzer GND

**Typ:** Passiver Piezo-Buzzer (PWM-gesteuert)

---

### GPIO (Optional: DHT11 Temperatur/Luftfeuchte)
- **GPIO4** (Pin 7) → DHT11 Data
- **3.3V** (Pin 1) → DHT11 VCC
- **GND** (Pin 9) → DHT11 GND

---

## Pin-Übersicht Tabelle

| GPIO | Pin | Funktion | Komponente | Anschluss |
|------|-----|----------|------------|-----------|
| GPIO2 | 3 | I²C SDA | MPU-9250, BMP180 | SDA |
| GPIO3 | 5 | I²C SCL | MPU-9250, BMP180 | SCL |
| GPIO14 | 8 | UART TXD | GPS NEO-M8N | RX |
| GPIO15 | 10 | UART RXD | GPS NEO-M8N | TX |
| GPIO10 | 19 | SPI MOSI | ePaper Display | DIN |
| GPIO11 | 23 | SPI SCLK | ePaper Display | CLK |
| GPIO8 | 24 | SPI CE0 | ePaper Display | CS |
| GPIO25 | 22 | GPIO | ePaper Display | DC |
| GPIO24 | 18 | GPIO | ePaper Display | RST |
| GPIO17 | 11 | GPIO | ePaper Display | BUSY |
| GPIO5 | 29 | GPIO | Drehencoder | CLK |
| GPIO27 | 13 | GPIO | Drehencoder | DT |
| GPIO6 | 31 | GPIO | Drehencoder | SW |
| GPIO22 | 15 | GPIO | Buzzer | Signal |
| GPIO4 | 7 | GPIO | DHT11 (optional) | Data |

---

## Verkabelung Checkliste

### Vor dem Anschließen:
- [ ] Raspberry Pi ist **AUSGESCHALTET**
- [ ] Alle Komponenten auf **3.3V** geprüft (kein 5V!)
- [ ] Richtige GPIO-Pins gemäß Tabelle identifiziert
- [ ] Dupont-Kabel oder Breadboard bereit

### Reihenfolge beim Anschließen:
1. **Zuerst GND** von allen Komponenten an Pi GND
2. **Dann VCC** (3.3V) von allen Komponenten
3. **Zuletzt Signal-Pins** (I²C, UART, SPI, GPIO)

### Nach dem Anschließen:
- [ ] Alle Verbindungen visuell prüfen
- [ ] Keine Kurzschlüsse zwischen 3.3V und GND
- [ ] Komponenten sitzen fest
- [ ] Erst dann Pi einschalten

---

## Raspberry Pi OS Konfiguration

### Interfaces aktivieren

```bash
sudo raspi-config
```

**Interface Options:**
- [ ] **I²C** → Enable
- [ ] **SPI** → Enable
- [ ] **Serial Port** → Enable (für GPS)
  - Serial Console → Disable (wichtig!)
  - Serial Hardware → Enable

**Nach Änderungen:** Reboot erforderlich

### Testen der Interfaces

**I²C-Test:**
```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```
Erwartete Ausgabe:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77
```
→ `0x68` = MPU-9250, `0x77` = BMP180

**UART-Test (GPS):**
```bash
cat /dev/ttyS0
```
→ Sollte NMEA-Sätze ausgeben (z.B. `$GPGGA,...`)

**SPI-Test:**
```bash
ls /dev/spidev*
```
→ Sollte `/dev/spidev0.0` und `/dev/spidev0.1` zeigen

---

## Schaltplan

```
                    ┌──────────────────┐
                    │ Raspberry Pi     │
                    │ Zero 2 W         │
                    └──────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌─────▼────┐      ┌─────▼────┐
   │ GPS      │      │ I²C Bus  │      │ SPI Bus  │
   │ NEO-M8N  │      │          │      │          │
   │          │      ├──────────┤      │          │
   │ UART     │      │ MPU-9250 │      │ ePaper   │
   │ 9600 bps │      │ (0x68)   │      │ Display  │
   └──────────┘      │          │      │ 296x128  │
                     │ BMP180   │      └──────────┘
                     │ (0x77)   │
                     └──────────┘
                           │
                     ┌─────▼────┐
                     │ GPIO     │
                     │          │
                     │ Encoder  │
                     │ Buzzer   │
                     │ (DHT11)  │
                     └──────────┘
```

---

## Gehäuse-Platzierung

**Wichtig für GPS-Empfang:**

```
┌─────────────────┐  ← Oben: GPS-Antenne
│   GPS Module    │     (freie Sicht zum Himmel!)
├─────────────────┤
│   ePaper Display│
│   (sichtbar)    │
├─────────────────┤
│  Raspberry Pi   │
│  Zero 2 W       │
├─────────────────┤
│  MPU-9250       │
│  BMP180         │
├─────────────────┤
│  Powerbank      │  ← Unten: Akku (Gewicht)
└─────────────────┘
```

**GPS-Antenne MUSS oben sein!** Sonst schlechter Empfang.

---

## Fehlersuche

### I²C funktioniert nicht
- `i2cdetect -y 1` zeigt keine Geräte
- **Lösung:** I²C in `raspi-config` aktivieren, Reboot

### GPS sendet keine Daten
- `cat /dev/ttyS0` zeigt nichts
- **Lösung:** Serial Console deaktivieren, Serial Hardware aktivieren

### Display bleibt schwarz
- **Lösung:** SPI aktivieren, Pins prüfen (besonders DC, RST, CS)

### Drehencoder reagiert nicht
- **Lösung:** Pull-Up in Software aktivieren oder externe 10kΩ Pull-Ups

---

## Sicherheitshinweise

⚠️ **WICHTIG:**
- **NIEMALS 5V an 3.3V Pins!** → Zerstört den Pi
- **NIEMALS GPIO-Pins direkt kurzschließen**
- **IMMER Pi ausschalten** vor Verkabelungsänderungen
- **GPS-Modul ist 3.3V** (nicht 5V!)
- **ePaper Display ist empfindlich** gegen statische Entladung

---

## Weitere Ressourcen

- [Offizielle Raspberry Pi GPIO-Dokumentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [pinout.xyz](https://pinout.xyz/) - Interaktive Pin-Referenz
- [u-blox NEO-M8N Datasheet](https://www.u-blox.com/en/product/neo-m8-series)
- [MPU-9250 Register Map](https://invensense.tdk.com/products/motion-tracking/9-axis/mpu-9250/)
- [Waveshare ePaper Wiki](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
