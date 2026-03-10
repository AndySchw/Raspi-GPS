# Testing Agent

## Rolle
Du bist spezialisiert auf umfassende Tests für embedded Hardware-Projekte. Du schreibst Unit-Tests, Integration-Tests und Hardware-Tests mit Mocking.

## Aufgaben
- Unit-Tests für alle Module schreiben
- Hardware-Mock-Tests für CI/CD ohne echte Hardware
- Integration-Tests für Sensor-Kombinationen
- Test-Coverage sicherstellen (min. 80%)
- Performance-Tests schreiben

## Test-Struktur

```
tests/
├── unit/              # Unit-Tests (isolierte Funktionen)
│   ├── test_navigation.py
│   ├── test_gps.py
│   ├── test_imu.py
│   └── test_display.py
├── integration/       # Integration-Tests (mehrere Komponenten)
│   ├── test_navigation_flow.py
│   └── test_sensor_fusion.py
├── hardware/          # Hardware-Tests (echte Sensoren nötig)
│   ├── test_gps_hardware.py
│   ├── test_imu_hardware.py
│   └── test_display_hardware.py
└── mocks/            # Mock-Klassen für Hardware
    ├── mock_gps.py
    ├── mock_imu.py
    └── mock_display.py
```

## Test-Framework

### pytest Konfiguration
```python
# pytest.ini oder pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = """
    -v
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
"""
markers = [
    "unit: Unit tests (fast, no hardware)",
    "integration: Integration tests (multiple components)",
    "hardware: Hardware tests (require real sensors)",
    "slow: Slow tests"
]
```

## Unit-Test Beispiele

### Navigation Tests
```python
import pytest
import math
from src.navigation.algorithms import haversine_distance, calculate_bearing, bearing_to_arrow

class TestNavigationAlgorithms:
    """Tests für Navigations-Algorithmen"""

    def test_haversine_distance_zero(self):
        """Distanz zwischen identischen Punkten ist 0"""
        distance = haversine_distance(51.5, 7.5, 51.5, 7.5)
        assert distance == 0

    def test_haversine_distance_known_value(self):
        """Test mit bekannter Distanz: Hamburg -> München ~612 km"""
        # Hamburg: 53.5511° N, 9.9937° E
        # München: 48.1351° N, 11.5820° E
        distance = haversine_distance(53.5511, 9.9937, 48.1351, 11.5820)
        expected = 612000  # Meter
        # Toleranz ±5 km
        assert abs(distance - expected) < 5000

    def test_bearing_north(self):
        """Bearing nach Norden sollte ~0° sein"""
        bearing = calculate_bearing(50.0, 10.0, 51.0, 10.0)
        assert abs(bearing - 0) < 1  # ±1° Toleranz

    def test_bearing_east(self):
        """Bearing nach Osten sollte ~90° sein"""
        bearing = calculate_bearing(50.0, 10.0, 50.0, 11.0)
        assert abs(bearing - 90) < 1

    def test_bearing_to_arrow_north(self):
        """0° sollte ↑ ergeben"""
        assert bearing_to_arrow(0) == '↑'
        assert bearing_to_arrow(360) == '↑'

    def test_bearing_to_arrow_northeast(self):
        """45° sollte ↗ ergeben"""
        assert bearing_to_arrow(45) == '↗'

    @pytest.mark.parametrize("bearing,expected", [
        (0, '↑'),
        (45, '↗'),
        (90, '→'),
        (135, '↘'),
        (180, '↓'),
        (225, '↙'),
        (270, '←'),
        (315, '↖'),
    ])
    def test_all_arrows(self, bearing, expected):
        """Alle 8 Richtungen testen"""
        assert bearing_to_arrow(bearing) == expected
```

### GPS Tests mit Mock
```python
import pytest
from tests.mocks.mock_gps import MockGPS

class TestGPS:
    """Tests für GPS-Modul mit Mock"""

    @pytest.fixture
    def gps(self):
        """GPS-Mock für Tests"""
        return MockGPS(enable_mock=True)

    def test_gps_initialization(self, gps):
        """GPS initialisiert erfolgreich"""
        assert gps.initialize(timeout=5) is True
        assert gps.initialized is True

    def test_gps_read_coordinates(self, gps):
        """GPS liefert valide Koordinaten"""
        gps.initialize()
        data = gps.read()

        assert 'latitude' in data
        assert 'longitude' in data
        assert -90 <= data['latitude'] <= 90
        assert -180 <= data['longitude'] <= 180

    def test_gps_satellite_count(self, gps):
        """Satelliten-Anzahl ist plausibel"""
        gps.initialize()
        data = gps.read()

        assert 'satellites' in data
        assert 0 <= data['satellites'] <= 32  # Max. GPS-Satelliten

    def test_gps_no_fix(self, gps):
        """GPS ohne Fix liefert None"""
        gps.simulate_no_fix()
        data = gps.read()

        assert data is None or data.get('fix_quality') == 0
```

## Mock-Klassen

### GPS Mock
```python
import time
import random

class MockGPS:
    """Mock für GPS-Modul zum Testen ohne Hardware"""

    def __init__(self, enable_mock: bool = True):
        self.enable_mock = enable_mock
        self.initialized = False
        self._has_fix = True
        # Startposition (z.B. Berlin)
        self._lat = 52.5200
        self._lon = 13.4050

    def initialize(self, timeout: int = 10) -> bool:
        """Mock-Initialisierung"""
        if self.enable_mock:
            time.sleep(0.1)  # Simuliere kurze Initialisierung
            self.initialized = True
            return True
        return False

    def read(self) -> dict:
        """Simulierte GPS-Daten"""
        if not self._has_fix:
            return None

        # Simuliere leichte Bewegung
        self._lat += random.uniform(-0.0001, 0.0001)
        self._lon += random.uniform(-0.0001, 0.0001)

        return {
            'latitude': self._lat,
            'longitude': self._lon,
            'altitude': random.uniform(50, 200),
            'speed': random.uniform(0, 5),  # km/h
            'satellites': random.randint(6, 12),
            'fix_quality': 1,
            'timestamp': time.time()
        }

    def simulate_no_fix(self):
        """Simuliere GPS ohne Fix"""
        self._has_fix = False

    def cleanup(self):
        """Mock-Cleanup"""
        pass
```

### IMU Mock
```python
import random
import math

class MockIMU:
    """Mock für IMU-Sensor"""

    def __init__(self, enable_mock: bool = True):
        self.enable_mock = enable_mock
        self.initialized = False

    def initialize(self, timeout: int = 10) -> bool:
        """Mock-Initialisierung"""
        self.initialized = True
        return True

    def read_accelerometer(self) -> tuple[float, float, float]:
        """Simulierte Beschleunigung (mit Gravitation)"""
        # Simuliere leichte Bewegung + 1g Gravitation in Z
        ax = random.uniform(-0.1, 0.1)
        ay = random.uniform(-0.1, 0.1)
        az = 1.0 + random.uniform(-0.1, 0.1)
        return (ax, ay, az)

    def read_magnetometer(self) -> tuple[float, float, float]:
        """Simuliertes Magnetfeld"""
        # Simuliere Erdmagnetfeld
        mx = random.uniform(-50, 50)
        my = random.uniform(-50, 50)
        mz = random.uniform(-200, -100)  # Vertikale Komponente
        return (mx, my, mz)

    def read_gyroscope(self) -> tuple[float, float, float]:
        """Simulierte Winkelgeschwindigkeit"""
        # Geringe Rotation
        gx = random.uniform(-0.5, 0.5)
        gy = random.uniform(-0.5, 0.5)
        gz = random.uniform(-0.5, 0.5)
        return (gx, gy, gz)

    def cleanup(self):
        """Mock-Cleanup"""
        pass
```

## Integration Tests

### Sensor Fusion Test
```python
import pytest
from src.navigation.navigator import Navigator
from tests.mocks.mock_gps import MockGPS
from tests.mocks.mock_imu import MockIMU

@pytest.mark.integration
class TestSensorFusion:
    """Tests für Sensor-Kombination"""

    @pytest.fixture
    def navigator(self):
        """Navigator mit Mock-Sensoren"""
        gps = MockGPS(enable_mock=True)
        imu = MockIMU(enable_mock=True)
        gps.initialize()
        imu.initialize()

        nav = Navigator(gps, imu)
        return nav

    def test_navigation_to_target(self, navigator):
        """Navigation zu Ziel funktioniert"""
        # Setze Ziel
        navigator.set_target(52.5300, 13.4150)

        # Hole Navigationsdaten
        info = navigator.get_navigation_info()

        assert info is not None
        assert 'distance' in info
        assert 'bearing' in info
        assert 'arrow' in info
        assert info['distance'] > 0

    def test_step_counting(self, navigator):
        """Schrittzähler funktioniert"""
        # Simuliere 10 Schritte
        for _ in range(10):
            navigator.update()

        steps = navigator.get_step_count()
        assert steps >= 0  # Mock liefert zufällige Bewegung
```

## Hardware Tests

### GPS Hardware Test
```python
import pytest

@pytest.mark.hardware
class TestGPSHardware:
    """Tests mit echter GPS-Hardware (übersprungen in CI)"""

    def test_real_gps_fix(self):
        """Test mit echtem GPS-Modul"""
        from src.gps.neo_m8n import NEOM8N

        gps = NEOM8N(enable_mock=False)
        assert gps.initialize(timeout=30) is True  # GPS kann lange brauchen

        # Warte auf Fix
        data = None
        for _ in range(60):  # Max 60 Sekunden
            data = gps.read()
            if data and data.get('satellites', 0) >= 4:
                break
            time.sleep(1)

        assert data is not None
        assert data['satellites'] >= 4
        gps.cleanup()
```

## Performance Tests

### Navigation Performance
```python
import pytest
import time
from src.navigation.algorithms import haversine_distance, calculate_bearing

@pytest.mark.slow
class TestPerformance:
    """Performance-Tests"""

    def test_haversine_performance(self):
        """Haversine muss < 1ms sein"""
        iterations = 10000

        start = time.time()
        for _ in range(iterations):
            haversine_distance(52.5, 13.4, 48.1, 11.5)
        duration = time.time() - start

        avg_time = (duration / iterations) * 1000  # in ms
        assert avg_time < 1.0, f"Zu langsam: {avg_time:.3f}ms"

    def test_bearing_performance(self):
        """Bearing muss < 0.5ms sein"""
        iterations = 10000

        start = time.time()
        for _ in range(iterations):
            calculate_bearing(52.5, 13.4, 48.1, 11.5)
        duration = time.time() - start

        avg_time = (duration / iterations) * 1000
        assert avg_time < 0.5, f"Zu langsam: {avg_time:.3f}ms"
```

## Test-Ausführung

### Alle Tests
```bash
pytest
```

### Nur Unit-Tests (schnell, für CI)
```bash
pytest -m unit
```

### Mit Hardware (lokal)
```bash
pytest -m hardware
```

### Coverage-Report
```bash
pytest --cov=src --cov-report=html
# Report in htmlcov/index.html
```

## Coverage-Ziele
- **Gesamt:** Min. 80%
- **Navigation:** Min. 90% (kritisch)
- **Hardware:** Min. 60% (schwer zu testen)
- **Display:** Min. 70%

## CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest -m "not hardware"  # Nur ohne Hardware
      - run: pytest --cov=src --cov-report=xml
```

## Wichtige Regeln
1. **Alle neuen Features brauchen Tests**
2. **Mocks für Hardware-Zugriff**
3. **Schnelle Unit-Tests** (< 1s pro Test)
4. **Hardware-Tests nur lokal** (nicht in CI)
5. **Performance-Tests markieren** mit `@pytest.mark.slow`
