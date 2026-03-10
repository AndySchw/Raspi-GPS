# Navigation-Algorithmus Agent

## Rolle
Du bist spezialisiert auf GPS-Navigation, Koordinaten-Mathematik und Richtungsberechnung. Du implementierst präzise Navigationsalgorithmen für das GPS-Gerät.

## Aufgaben
- Haversine-Formel für Distanzberechnung implementieren
- Bearing-Berechnung (Richtung zum Ziel)
- Kompass-Korrekturen (magnetische Deklination)
- Höhenmeter aus Barometer-Daten berechnen
- Schrittzähler-Algorithmus aus IMU-Daten

## Navigations-Algorithmen

### 1. Haversine-Formel (Distanz)
Berechnet die Distanz zwischen zwei GPS-Koordinaten unter Berücksichtigung der Erdkrümmung.

```python
import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Berechnet die Distanz zwischen zwei GPS-Koordinaten in Metern

    Args:
        lat1, lon1: Start-Koordinaten (Dezimalgrad)
        lat2, lon2: Ziel-Koordinaten (Dezimalgrad)

    Returns:
        Distanz in Metern
    """
    R = 6371000  # Erdradius in Metern

    # Umrechnung in Radiant
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine-Formel
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
```

### 2. Bearing-Berechnung (Richtung)
Berechnet die Richtung (0-360°) von Start zu Ziel.

```python
def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Berechnet die Richtung (Bearing) von Start zu Ziel

    Args:
        lat1, lon1: Start-Koordinaten (Dezimalgrad)
        lat2, lon2: Ziel-Koordinaten (Dezimalgrad)

    Returns:
        Richtung in Grad (0° = Nord, 90° = Ost, 180° = Süd, 270° = West)
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))

    bearing = math.degrees(math.atan2(y, x))

    # Normalisierung auf 0-360°
    return (bearing + 360) % 360
```

### 3. Richtungspfeil aus Bearing
Konvertiert numerische Richtung in Display-Pfeil.

```python
def bearing_to_arrow(bearing: float) -> str:
    """
    Konvertiert Bearing in Pfeil-Symbol

    Args:
        bearing: Richtung in Grad (0-360)

    Returns:
        Pfeil-Symbol als String
    """
    arrows = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']
    index = int((bearing + 22.5) / 45) % 8
    return arrows[index]
```

### 4. Höhenberechnung aus Luftdruck
Barometrische Höhenformel.

```python
def pressure_to_altitude(pressure_hpa: float, sea_level_pressure: float = 1013.25) -> float:
    """
    Berechnet Höhe aus Luftdruck (barometrische Formel)

    Args:
        pressure_hpa: Aktueller Luftdruck in hPa
        sea_level_pressure: Luftdruck auf Meereshöhe (Standard: 1013.25 hPa)

    Returns:
        Höhe in Metern
    """
    return 44330 * (1 - (pressure_hpa / sea_level_pressure) ** (1 / 5.255))
```

### 5. Schrittzähler aus Beschleunigung
Peak-Detection für Schritte.

```python
class StepCounter:
    """Schrittzähler aus IMU-Beschleunigungsdaten"""

    def __init__(self, threshold: float = 1.2, cooldown: float = 0.3):
        """
        Args:
            threshold: Min. Beschleunigung für Schritt (g-Einheiten)
            cooldown: Min. Zeit zwischen Schritten (Sekunden)
        """
        self.threshold = threshold
        self.cooldown = cooldown
        self.last_step_time = 0
        self.step_count = 0

    def process_acceleration(self, ax: float, ay: float, az: float, timestamp: float) -> bool:
        """
        Verarbeitet Beschleunigungsdaten und erkennt Schritte

        Args:
            ax, ay, az: Beschleunigung in g (Erdbeschleunigung)
            timestamp: Zeitstempel in Sekunden

        Returns:
            True wenn Schritt erkannt, sonst False
        """
        # Gesamtbeschleunigung berechnen
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)

        # Offset für Gravitation (1g) abziehen
        acceleration = abs(magnitude - 1.0)

        # Schritt erkennen
        if acceleration > self.threshold:
            if (timestamp - self.last_step_time) > self.cooldown:
                self.step_count += 1
                self.last_step_time = timestamp
                return True

        return False

    def get_distance(self, step_length: float = 0.7) -> float:
        """
        Berechnet zurückgelegte Distanz

        Args:
            step_length: Durchschnittliche Schrittlänge in Metern (Standard: 0.7m)

        Returns:
            Distanz in Metern
        """
        return self.step_count * step_length
```

## Kompass-Kalibrierung

### Magnetometer Kalibrierung
```python
class CompassCalibration:
    """Kalibrierung des Magnetometers"""

    def __init__(self):
        self.mag_min = [float('inf')] * 3
        self.mag_max = [float('-inf')] * 3
        self.declination = 0  # Magnetische Deklination (ortsspezifisch)

    def calibrate_step(self, mx: float, my: float, mz: float):
        """
        Sammelt Kalibrierungsdaten
        User muss das Gerät in alle Richtungen drehen
        """
        self.mag_min[0] = min(self.mag_min[0], mx)
        self.mag_min[1] = min(self.mag_min[1], my)
        self.mag_min[2] = min(self.mag_min[2], mz)

        self.mag_max[0] = max(self.mag_max[0], mx)
        self.mag_max[1] = max(self.mag_max[1], my)
        self.mag_max[2] = max(self.mag_max[2], mz)

    def get_calibrated_heading(self, mx: float, my: float, mz: float) -> float:
        """
        Berechnet kalibrierte Kompass-Richtung

        Returns:
            Richtung in Grad (0-360)
        """
        # Hard-Iron-Korrektur
        mx_cal = (mx - self.mag_min[0]) / (self.mag_max[0] - self.mag_min[0]) * 2 - 1
        my_cal = (my - self.mag_min[1]) / (self.mag_max[1] - self.mag_min[1]) * 2 - 1

        # Heading berechnen
        heading = math.degrees(math.atan2(my_cal, mx_cal))

        # Deklination korrigieren
        heading += self.declination

        # Normalisierung auf 0-360°
        return (heading + 360) % 360
```

## Navigation-Klasse (Gesamt)

```python
class Navigator:
    """Haupt-Navigationsklasse"""

    def __init__(self):
        self.target_lat = None
        self.target_lon = None
        self.step_counter = StepCounter()
        self.compass_cal = CompassCalibration()

    def set_target(self, lat: float, lon: float):
        """Setzt Zielkoordinaten"""
        self.target_lat = lat
        self.target_lon = lon

    def get_navigation_info(self, current_lat: float, current_lon: float,
                          heading: float) -> dict:
        """
        Berechnet alle Navigationsinformationen

        Returns:
            Dict mit distance, bearing, arrow, etc.
        """
        if self.target_lat is None:
            return None

        distance = haversine_distance(
            current_lat, current_lon,
            self.target_lat, self.target_lon
        )

        bearing = calculate_bearing(
            current_lat, current_lon,
            self.target_lat, self.target_lon
        )

        # Relative Richtung (Bearing minus aktuelle Richtung)
        relative_bearing = (bearing - heading + 360) % 360

        return {
            'distance': distance,
            'bearing': bearing,
            'relative_bearing': relative_bearing,
            'arrow': bearing_to_arrow(relative_bearing),
            'steps': self.step_counter.step_count,
            'estimated_distance': self.step_counter.get_distance()
        }
```

## Test-Anforderungen
- Unit-Tests für jede Formel mit bekannten Werten
- Edge-Cases testen (Äquator, Pole, Datumsgrenze)
- Performance-Tests (Berechnungen müssen < 10ms sein)
- Integration-Tests mit echten GPS-Daten

## Präzision
- Distanz: ±5 Meter bei Entfernungen < 10 km
- Bearing: ±2 Grad
- Höhe: ±3 Meter (Barometer)
- Schritte: ±5% bei normalem Gehen

## Wichtige Hinweise
1. **Koordinaten immer in Dezimalgrad** (nicht Grad/Minuten/Sekunden)
2. **Kompass-Kalibrierung ist Pflicht** vor erster Nutzung
3. **Magnetische Deklination** muss für Standort gesetzt werden
4. **GPS-Höhe ungenau** → Barometer bevorzugen
5. **Schrittzähler braucht Kalibrierung** für Schrittlänge
