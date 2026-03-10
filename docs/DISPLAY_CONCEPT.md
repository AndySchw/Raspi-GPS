# Display-Konzept: Screen-Layouts & Navigation

## 📺 Hardware: 2.9" ePaper (296×128 Pixel, S/W)

**Eigenschaften:**
- Sehr gut lesbar im Sonnenlicht ☀️
- Geringer Stromverbrauch (~4mA aktiv, 0µA sleep)
- Refresh: ~2s (Full), ~0.3s (Partial)
- Kein Backlight nötig

---

## 🎨 Screen-Design Philosophie

**Prinzipien:**
1. **Große Schrift** - outdoor-lesbar
2. **Hoher Kontrast** - nur Schwarz/Weiß
3. **Deutsche Beschriftungen** - alles auf Deutsch 🇩🇪
4. **Klare Hierarchie** - wichtigste Info zuerst
5. **Batterie-bewusst** - nur Updates wenn nötig

---

## 📱 Screen-Struktur

### Hauptmenü-Ebenen

```
Hauptmenü
├── 1. GPS-Status          ← Koordinaten, Höhe, Satelliten
├── 2. Navigation          ← Richtung zum Ziel
├── 3. Kompass             ← Himmelsrichtung
├── 4. Tracking            ← Aufzeichnung
├── 5. Karte (optional)    ← OSM-Ansicht
├── 6. Statistiken         ← Touren-Übersicht
└── 7. Einstellungen       ← Konfiguration
```

**Navigation:**
- **Drehen:** Nächster/Vorheriger Screen
- **Drücken:** Screen auswählen / Zurück

---

## 🖼️ Screen-Layouts (Detailliert)

### Screen 1: GPS-Status ⭐ START-SCREEN

```
┌─────────────────────────────┐
│ GPS                   12:34 │ ← Header: Name + Uhrzeit
├─────────────────────────────┤
│                             │
│ Breite:  52.520008° N       │ ← Deutsch! Nord/Süd
│ Länge:    13.404954° O      │ ← Ost/West
│                             │
│ Höhe:    183 m ü.NN         │ ← über Normal-Null
│ Geschw:  4.2 km/h           │ ← Geschwindigkeit
│                             │
│ Satelliten: [●●●●●●●●○○]    │ ← Visuell
│             10/12  GPS+GLO  │ ← Multi-GNSS
│                             │
│ Genauigkeit: ± 2.5 m        │ ← HDOP basiert
└─────────────────────────────┘
```

**Daten-Quellen:**
- GPS NEO-M8N: Lat, Lon, Speed, Sats
- BMP180: Höhe (präziser als GPS)
- Berechnet: Genauigkeit aus HDOP

**Update:** Alle 2 Sekunden

---

### Screen 2: Navigation ⭐ KERNFUNKTION

```
┌─────────────────────────────┐
│ → Zum Ziel            12:35 │
├─────────────────────────────┤
│                             │
│           ↗                 │ ← GROSSER Pfeil (48pt)
│        Nordost              │ ← Himmelsrichtung
│                             │
│    Entfernung: 324 m        │ ← Distanz
│    Richtung:   42°          │ ← Bearing
│                             │
│ ████████████░░░░░░  67%     │ ← Fortschritt
│                             │
│ Geschätzt: 4 Min  @ 4km/h  │ ← ETA
└─────────────────────────────┘
```

**Logik:**
```python
# Haversine für Distanz
distance = haversine(current_pos, target_pos)

# Bearing für Richtung
bearing = calculate_bearing(current_pos, target_pos)

# Relativer Pfeil (minus Kompass-Richtung)
arrow_direction = bearing - compass_heading

# Fortschritt
progress = 1 - (distance / start_distance)

# ETA
eta = distance / current_speed
```

**Pfeil-Symbole:**
- ↑ Nord (0°)
- ↗ Nordost (45°)
- → Ost (90°)
- ↘ Südost (135°)
- ↓ Süd (180°)
- ↙ Südwest (225°)
- ← West (270°)
- ↖ Nordwest (315°)

**Update:** Jede Sekunde (bei Bewegung)

---

### Screen 3: Kompass 🧭

```
┌─────────────────────────────┐
│ Kompass               12:36 │
├─────────────────────────────┤
│          N                  │
│          │                  │
│      NW  │  NO              │
│        ╲ │ ╱                │
│    W ────●──── O            │ ← Kompass-Rose
│        ╱ ↑ ╲                │ ← Deine Richtung
│      SW  │  SO              │
│          │                  │
│          S                  │
│                             │
│ Blickrichtung: 42° NO       │ ← MPU-9250 Magnetometer
│ Ziel: ○ 324m in NW          │ ← Wenn Ziel gesetzt
└─────────────────────────────┘
```

**Daten-Quelle:**
- MPU-9250 Magnetometer
- Kalibrierung beim Start
- Magnetische Deklination korrigiert

**Update:** 10 Hz (flüssig)

---

### Screen 4: Tracking 📍 ●REC

```
┌─────────────────────────────┐
│ ●REC Aufzeichnung     12:37 │ ← Blinkt bei Recording
├─────────────────────────────┤
│                             │
│ Dauer:      01:23:45        │ ← Live Timer
│ Strecke:    2.4 km          │ ← GPS-basiert
│ Schritte:   3420            │ ← IMU Schrittzähler
│                             │
│ ↑ Aufstieg:   145 m         │ ← Barometer
│ ↓ Abstieg:    78 m          │
│                             │
│ Ø Tempo:    4.2 km/h        │
│ Max. Höhe:  215 m           │
│                             │
│ [Pause] [Stop] [Speichern] │ ← Encoder-Menü
└─────────────────────────────┘
```

**Features:**
- Start/Stop per Encoder-Druck (langes Drücken)
- Auto-Save alle 60 Sekunden
- Log-Interval: 5 Sekunden (konfigurierbar)
- GPX-Export bei Stop

**Daten:**
```json
{
  "timestamp": "2024-03-09T12:37:00Z",
  "lat": 52.520008,
  "lon": 13.404954,
  "altitude": 183,
  "speed": 4.2,
  "steps": 3420
}
```

---

### Screen 5: Karte 🗺️ (Optional, später)

```
┌─────────────────────────────┐
│ Karte    [±] Z:14    12:38  │ ← Zoom-Stufe
├─────────────────────────────┤
│         N↑                  │
│   ╱╲   ╱╲  Wald             │
│  ╱  ╲ ╱  ╲                  │
│ ╱____╲____╲                 │
│                             │
│     ●  Du (183m)            │ ← Deine Position
│     ↑  4.2 km/h             │
│  ━━━━━━━  Weg               │
│                             │
│  ⌂         ○                │ ← Gebäude, Ziel
│     Ziel: 420m NO           │
│                             │
│ Offline OSM    52.52/13.40  │ ← Koordinaten
└─────────────────────────────┘
```

**Karten-System:**

**Tiles (256×256 px):**
```
data/maps/
  ├── tiles/
  │   ├── 14/8808/5372.png    ← Zoom 14
  │   ├── 14/8808/5373.png
  │   └── ...
  └── metadata.json
```

**Rendering:**
```python
# 1. Berechne welche Tiles sichtbar sind
visible_tiles = calculate_visible_tiles(lat, lon, zoom, display_size)

# 2. Lade Tiles von SD
tiles = load_tiles(visible_tiles)

# 3. Zeichne auf Display
render_map(tiles, current_position)

# 4. Overlay: Position, Ziel, Track
draw_overlay(position, target, track_points)
```

**Zoom-Stufen:**
- **12:** Überblick (~5 km Radius)
- **14:** Standard (~1 km Radius) ⭐
- **16:** Detail (~250 m Radius)

**Steuerung:**
- Drehen: Zoom +/-
- Drücken: Zurück zum Standard-Zoom

**Speicherbedarf (Beispiele):**
```
Köln 20×20 km, Zoom 12-16:
→ ~150 MB auf SD

Wandergebiet 50×50 km, Zoom 12-16:
→ ~400 MB auf SD

Mehrere Regionen mit 64GB locker möglich! ✅
```

---

### Screen 6: Statistiken 📊

```
┌─────────────────────────────┐
│ Statistiken           12:39 │
├─────────────────────────────┤
│ Heute (09.03.2024):         │
│  Strecke:     12.4 km       │
│  Zeit:        03:24:15      │
│  Schritte:    17.820        │
│  Höhenmeter:  ↑320m / ↓180m │
│                             │
│ Letzte 7 Tage:              │
│  Touren:      5             │
│  Strecke:     48.2 km       │
│  Ø pro Tour:  9.6 km        │
│                             │
│ Gesamt (alle Zeiten):       │
│  Touren:      127           │
│  Strecke:     1.248 km      │
└─────────────────────────────┘
```

**Daten-Quelle:**
- Aus gespeicherten Tracks (JSON/GPX)
- Berechnet beim Screen-Öffnen

---

### Screen 7: Höhenprofil ⛰️

```
┌─────────────────────────────┐
│ Höhenprofil           12:40 │
├─────────────────────────────┤
│                             │
│ 220m┤      ╱╲                │
│     │     ╱  ╲               │
│ 200m┤    ╱    ╲╲             │
│     │   ╱      ╲             │
│ 180m┤  ╱        ╲╲           │
│     │ ╱          ╲           │
│ 160m┼●────────────●──────    │ ← Du bist hier
│     0────1────2────3────4km  │
│                             │
│ Aktuell: 183m   Steigung:   │
│ Start: 165m     ▲ 12 m/min  │
└─────────────────────────────┘
```

**Logik:**
```python
# Sammle Höhendaten aus Track
altitude_profile = [point.altitude for point in track]

# Zeichne als Linie
draw_line_graph(altitude_profile, width=296, height=90)

# Markiere aktuelle Position
mark_current_position(current_index)

# Berechne Steigung
slope = calculate_slope(last_5_points)
```

---

### Screen 8: Einstellungen ⚙️

```
┌─────────────────────────────┐
│ Einstellungen         12:41 │
├─────────────────────────────┤
│                             │
│ > Koordinaten-Format        │ ← Drehen = auswählen
│   [Dezimal] Grad/Min/Sek    │
│                             │
│   Display-Update            │
│   [2 Sek] 5 Sek  10 Sek     │
│                             │
│   Energie-Modus             │
│   [Normal] Sparsam  Ultra   │
│                             │
│   Helligkeit                │
│   [█████████░] 90%          │
│                             │
│ [Zurück] [Speichern]        │
└─────────────────────────────┘
```

**Settings werden in:**
- `config/user_settings.yaml` gespeichert
- Beim nächsten Start geladen

---

## 🎮 Bedienung: KY-040 Encoder

### Basis-Steuerung

```
┌─────────────────┐
│  Hauptmenü      │
│  1. GPS         │ ← Drehen nach oben
│> 2. Navigation  │ ← Aktuell
│  3. Kompass     │ ← Drehen nach unten
│  4. Tracking    │
└─────────────────┘

DREHEN:  Cursor hoch/runter
DRÜCKEN: Screen öffnen
```

### In einem Screen

```
┌─────────────────────────────┐
│ Navigation                  │
│                             │
│     Inhalt...               │
│                             │
│ [Zurück] [Ziel setzen]      │
└─────────────────────────────┘

DREHEN:  Zwischen Buttons wechseln
DRÜCKEN: Button aktivieren
LANG DRÜCKEN (2s): Zurück zum Hauptmenü
```

### Quick-Actions

**Von jedem Screen:**
- **Doppel-Drücken:** Zurück zum GPS-Screen
- **3× Drehen (schnell):** Display-Helligkeit
- **Lang drücken (5s):** Gerät ausschalten

---

## 🌍 Deutsche Formatierung

### Koordinaten

**Standard (Dezimalgrad):**
```python
def format_coordinate_german(lat: float, lon: float) -> str:
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "O" if lon >= 0 else "W"  # Ost, nicht E!

    return (
        f"Breite:  {abs(lat):.6f}° {lat_dir}\n"
        f"Länge:   {abs(lon):.6f}° {lon_dir}"
    )

# Output:
# Breite:  52.520008° N
# Länge:    13.404954° O
```

**Alternative (Grad/Minuten/Sekunden):**
```python
def format_dms_german(decimal: float, is_latitude: bool) -> str:
    degrees = int(abs(decimal))
    minutes = int((abs(decimal) - degrees) * 60)
    seconds = ((abs(decimal) - degrees) * 60 - minutes) * 60

    if is_latitude:
        direction = "N" if decimal >= 0 else "S"
    else:
        direction = "O" if decimal >= 0 else "W"

    return f"{degrees}°{minutes}'{seconds:.1f}\" {direction}"

# Output:
# 52°31'12.0" N
# 13°24'17.8" O
```

### Himmelsrichtungen

```python
DIRECTIONS_GERMAN = {
    0: "N",      # Nord
    45: "NO",    # Nordost
    90: "O",     # Ost
    135: "SO",   # Südost
    180: "S",    # Süd
    225: "SW",   # Südwest
    270: "W",    # West
    315: "NW"    # Nordwest
}

def bearing_to_german(bearing: float) -> str:
    # Runde auf nächste 45°
    index = int((bearing + 22.5) / 45) % 8
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    return DIRECTIONS_GERMAN[angles[index]]
```

### Distanzen

```python
def format_distance_german(meters: float) -> str:
    if meters < 1000:
        return f"{meters:.0f} m"
    else:
        return f"{meters/1000:.1f} km"

# Output:
# 324 m
# 2.4 km
```

### Höhe

```python
def format_altitude_german(meters: float) -> str:
    return f"{meters:.0f} m ü.NN"
    # ü.NN = über Normal-Null (Meeresspiegel)

# Output:
# 183 m ü.NN
```

### Geschwindigkeit

```python
def format_speed_german(mps: float) -> str:
    kmh = mps * 3.6
    return f"{kmh:.1f} km/h"

# Output:
# 4.2 km/h
```

### Zeit/Datum

```python
import datetime
import locale

# Deutsch einstellen
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

def format_datetime_german(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M:%S")

# Output:
# 09.03.2024 12:34:56
```

---

## 🔋 Energie-Optimierung

### Display-Update-Strategien

**Normal-Modus:** (12-15h Laufzeit)
```yaml
display:
  update_interval: 2.0        # 2 Sekunden
  full_refresh_every: 10      # Alle 10 Updates
```

**Spar-Modus:** (15-18h)
```yaml
display:
  update_interval: 5.0        # 5 Sekunden
  full_refresh_every: 20      # Weniger Full-Refreshs
```

**Ultra-Spar:** (20h+)
```yaml
display:
  update_interval: 10.0       # 10 Sekunden
  full_refresh_every: 30
```

### Smart-Updates

**Nur aktualisieren wenn:**
```python
def should_update_display(current_data, last_data) -> bool:
    # GPS-Position hat sich geändert (>5m)
    if distance(current_data.pos, last_data.pos) > 5:
        return True

    # Höhe hat sich geändert (>2m)
    if abs(current_data.altitude - last_data.altitude) > 2:
        return True

    # Richtung hat sich geändert (>10°)
    if abs(current_data.bearing - last_data.bearing) > 10:
        return True

    # Max. 5 Sekunden ohne Update
    if time.time() - last_update > 5:
        return True

    return False
```

### Screen-Schlaf

```python
# Display schläft nach 5 Min Inaktivität
if no_movement_for(300):  # 5 Minuten
    display.sleep()

# Aufwachen bei Bewegung oder Encoder-Druck
```

---

## 📐 Layout-Grid

**296×128 Pixel aufgeteilt:**

```
┌───────────────────────────────┐  ← 0px
│ Header (25px)                 │
├───────────────────────────────┤  ← 25px
│                               │
│                               │
│ Content Area (98px)           │
│                               │
│                               │
│                               │
├───────────────────────────────┤  ← 123px
│ Footer (5px)                  │
└───────────────────────────────┘  ← 128px
  0px                       296px
```

**Schriftgrößen:**
- **Header:** 14pt (Title), 10pt (Zeit)
- **Hauptinhalt:** 16pt (Standard), 48pt (Pfeil)
- **Klein:** 12pt (Footer, Zusatz-Info)

**Margins:**
- Links/Rechts: 5px
- Oben/Unten: 3px
- Zwischen Elementen: 5px

---

## 🎨 Icons & Symbole (Unicode)

### Pfeile
```
↑ ↗ → ↘ ↓ ↙ ← ↖
```

### Status
```
● REC-Indikator (rot bei Farb-Display)
○ Inaktiv
█ Batterie voll
░ Batterie leer
✓ Erfolg
✗ Fehler
```

### Navigation
```
⌂ Haus/Zuhause
⛰ Berg/Gipfel
~ Wasser
╱╲ Wald
━━ Straße/Weg
```

---

## 📊 Screen-Prioritäten

**Phase 1 (Basis):** Sofort implementieren
1. ✅ GPS-Status
2. ✅ Navigation
3. ✅ Tracking
4. ✅ Kompass

**Phase 2 (Erweitert):** Nach Basis-Test
5. ⚙️ Einstellungen
6. 📊 Statistiken
7. ⛰️ Höhenprofil

**Phase 3 (Optional):** Wenn gewünscht
8. 🗺️ Karte mit OSM-Tiles

---

## 🔄 Screen-Wechsel Flow

```mermaid
Start
  ↓
GPS-Status (Default)
  ↓ (drehen rechts)
Navigation
  ↓ (drehen rechts)
Kompass
  ↓ (drehen rechts)
Tracking
  ↓ (drehen rechts)
Einstellungen
  ↓ (drehen rechts)
Statistiken
  ↓ (drehen rechts)
Höhenprofil
  ↓ (drehen rechts)
[Karte - optional]
  ↓ (drehen rechts)
GPS-Status (Kreis schließt)
```

**Jederzeit:**
- Lang drücken (2s) → Zurück zu GPS-Status
- Doppel-drücken → Hauptmenü

---

## 🛠️ Implementation

**Struktur:**
```python
src/display/
├── epaper.py              # Hardware-Treiber
├── screen_manager.py      # Screen-Wechsel
├── renderer.py            # Basis-Rendering
├── screens/
│   ├── base_screen.py    # Basis-Klasse
│   ├── gps_screen.py
│   ├── navigation_screen.py
│   ├── compass_screen.py
│   ├── tracking_screen.py
│   ├── stats_screen.py
│   ├── settings_screen.py
│   └── map_screen.py     # Optional
└── widgets/
    ├── header.py         # Standard-Header
    ├── progress_bar.py
    ├── satellite_bar.py
    └── compass_rose.py
```

**Basis-Screen Klasse:**
```python
class BaseScreen:
    def __init__(self, display):
        self.display = display
        self.needs_update = True

    def render(self, data: dict) -> Image:
        """Rendert Screen, gibt PIL Image zurück"""
        raise NotImplementedError

    def on_encoder_rotate(self, direction: int):
        """Encoder wurde gedreht"""
        pass

    def on_encoder_press(self):
        """Encoder wurde gedrückt"""
        pass
```

---

**Stand:** 2024-03-09
**Version:** 1.0
**Status:** Konzept fertig, bereit für Implementation
