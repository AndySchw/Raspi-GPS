#!/usr/bin/env python3
"""
OpenStreetMap Tiles Downloader für offline Karten

Lädt OSM-Tiles für eine Region herunter und speichert sie auf der SD-Karte.

Verwendung:
    python scripts/download_maps.py --region "Köln" --zoom 12-16
    python scripts/download_maps.py --bbox 50.8,6.8,51.0,7.1 --zoom 14
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Tuple, List
import requests
from PIL import Image


class OSMTileDownloader:
    """OpenStreetMap Tile Downloader"""

    def __init__(self, output_dir: str = "data/maps", user_agent: str = "DIY-GPS-Device/1.0"):
        """
        Initialisiert Downloader

        Args:
            output_dir: Ziel-Verzeichnis für Tiles
            user_agent: User-Agent für OSM-Server (WICHTIG!)
        """
        self.output_dir = Path(output_dir)
        self.tiles_dir = self.output_dir / "tiles"
        self.tiles_dir.mkdir(parents=True, exist_ok=True)

        self.user_agent = user_agent
        self.tile_server = "https://tile.openstreetmap.org"  # OSM Standard-Server

        # Rate-Limiting (OSM Tile Usage Policy!)
        self.request_delay = 0.1  # 100ms zwischen Requests (max 10/s)

    def lat_lon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        Konvertiert Lat/Lon zu Tile-Koordinaten

        Args:
            lat: Latitude (Breite)
            lon: Longitude (Länge)
            zoom: Zoom-Level (0-19)

        Returns:
            (x, y) Tile-Koordinaten
        """
        lat_rad = math.radians(lat)
        n = 2 ** zoom
        x = int((lon + 180) / 360 * n)
        y = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
        return (x, y)

    def tile_to_lat_lon(self, x: int, y: int, zoom: int) -> Tuple[float, float]:
        """
        Konvertiert Tile-Koordinaten zu Lat/Lon

        Args:
            x, y: Tile-Koordinaten
            zoom: Zoom-Level

        Returns:
            (lat, lon)
        """
        n = 2 ** zoom
        lon = x / n * 360 - 180
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return (lat, lon)

    def get_bbox_tiles(self, lat_min: float, lon_min: float,
                       lat_max: float, lon_max: float, zoom: int) -> List[Tuple[int, int, int]]:
        """
        Berechnet alle Tiles in einer Bounding-Box

        Args:
            lat_min, lon_min: Südwest-Ecke
            lat_max, lon_max: Nordost-Ecke
            zoom: Zoom-Level

        Returns:
            Liste von (zoom, x, y) Tuples
        """
        x_min, y_max = self.lat_lon_to_tile(lat_min, lon_min, zoom)
        x_max, y_min = self.lat_lon_to_tile(lat_max, lon_max, zoom)

        tiles = []
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tiles.append((zoom, x, y))

        return tiles

    def download_tile(self, zoom: int, x: int, y: int) -> bool:
        """
        Lädt ein einzelnes Tile herunter

        Args:
            zoom, x, y: Tile-Koordinaten

        Returns:
            True wenn erfolgreich, False sonst
        """
        # Ziel-Pfad
        tile_path = self.tiles_dir / str(zoom) / str(x) / f"{y}.png"

        # Überspringe wenn bereits vorhanden
        if tile_path.exists():
            return True

        # URL
        url = f"{self.tile_server}/{zoom}/{x}/{y}.png"

        try:
            # Download mit User-Agent (WICHTIG für OSM!)
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Verzeichnis erstellen
                tile_path.parent.mkdir(parents=True, exist_ok=True)

                # Speichern
                with open(tile_path, 'wb') as f:
                    f.write(response.content)

                return True
            else:
                print(f"  ✗ Fehler {response.status_code} für Tile {zoom}/{x}/{y}")
                return False

        except Exception as e:
            print(f"  ✗ Exception: {e}")
            return False

    def download_region(self, lat_min: float, lon_min: float,
                       lat_max: float, lon_max: float,
                       zoom_min: int, zoom_max: int):
        """
        Lädt alle Tiles für eine Region

        Args:
            lat_min, lon_min: Südwest-Ecke
            lat_max, lon_max: Nordost-Ecke
            zoom_min, zoom_max: Zoom-Level Bereich
        """
        print(f"Download-Region:")
        print(f"  Bbox: {lat_min:.4f},{lon_min:.4f} → {lat_max:.4f},{lon_max:.4f}")
        print(f"  Zoom: {zoom_min}-{zoom_max}")
        print()

        total_tiles = 0
        downloaded = 0
        skipped = 0
        failed = 0

        for zoom in range(zoom_min, zoom_max + 1):
            tiles = self.get_bbox_tiles(lat_min, lon_min, lat_max, lon_max, zoom)
            total_tiles += len(tiles)

            print(f"Zoom {zoom}: {len(tiles)} Tiles")

            for i, (z, x, y) in enumerate(tiles):
                # Progress
                if i % 10 == 0:
                    progress = (i / len(tiles)) * 100
                    print(f"  Progress: {progress:.1f}% ({i}/{len(tiles)})", end='\r')

                # Download
                tile_path = self.tiles_dir / str(z) / str(x) / f"{y}.png"
                if tile_path.exists():
                    skipped += 1
                else:
                    if self.download_tile(z, x, y):
                        downloaded += 1
                    else:
                        failed += 1

                # Rate-Limiting
                time.sleep(self.request_delay)

            print(f"  Progress: 100.0% ({len(tiles)}/{len(tiles)})")
            print()

        # Zusammenfassung
        print("=" * 50)
        print(f"Download abgeschlossen!")
        print(f"  Gesamt: {total_tiles} Tiles")
        print(f"  ✓ Heruntergeladen: {downloaded}")
        print(f"  ○ Übersprungen: {skipped}")
        print(f"  ✗ Fehler: {failed}")
        print()

        # Speicherplatz
        size_mb = sum(f.stat().st_size for f in self.tiles_dir.rglob('*.png')) / (1024 * 1024)
        print(f"  Speicherplatz: {size_mb:.1f} MB")

        # Metadata speichern
        self.save_metadata(lat_min, lon_min, lat_max, lon_max, zoom_min, zoom_max)

    def save_metadata(self, lat_min: float, lon_min: float,
                     lat_max: float, lon_max: float,
                     zoom_min: int, zoom_max: int):
        """Speichert Metadata über heruntergeladene Region"""
        metadata = {
            "bbox": {
                "lat_min": lat_min,
                "lon_min": lon_min,
                "lat_max": lat_max,
                "lon_max": lon_max
            },
            "zoom": {
                "min": zoom_min,
                "max": zoom_max
            },
            "tile_server": self.tile_server,
            "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Metadata gespeichert: {metadata_path}")


# Vordefinierte Regionen
REGIONS = {
    # Städte (klein, ~20×20 km)
    "köln": (50.85, 6.85, 51.05, 7.05),
    "berlin": (52.35, 13.25, 52.65, 13.55),
    "münchen": (48.05, 11.45, 48.25, 11.65),
    "hamburg": (53.45, 9.85, 53.65, 10.15),
    "frankfurt": (50.00, 8.55, 50.20, 8.80),
    "düsseldorf": (51.15, 6.70, 51.30, 6.90),

    # Bundesländer (groß, ganze Regionen)
    "nrw": (50.32, 5.87, 52.53, 9.46),                    # NRW komplett (~400×250 km)
    "bayern": (47.27, 8.98, 50.56, 13.84),                # Bayern komplett
    "baden-württemberg": (47.53, 7.51, 49.79, 10.50),     # BW komplett
    "hessen": (49.40, 7.77, 51.66, 10.24),                # Hessen komplett
    "niedersachsen": (51.30, 6.65, 53.90, 11.60),         # Niedersachsen komplett

    # Regionen (mittel, ~100×100 km)
    "rheinland": (50.50, 6.50, 51.50, 7.50),              # Rheinland
    "ruhrgebiet": (51.30, 6.70, 51.70, 7.70),             # Ruhrgebiet
    "bergisches-land": (50.90, 7.00, 51.30, 7.50),        # Bergisches Land
    "eifel": (50.20, 6.20, 50.80, 7.00),                  # Eifel
    "sauerland": (51.00, 7.50, 51.50, 8.50),              # Sauerland
    "schwarzwald": (47.80, 7.80, 48.70, 8.50),            # Schwarzwald
    "harz": (51.50, 10.30, 51.90, 11.20),                 # Harz
    "allgäu": (47.30, 9.80, 47.80, 10.70),                # Allgäu
    "bodensee": (47.50, 8.80, 47.80, 9.70),               # Bodensee

    # Wander-Gebiete (klein/mittel)
    "siebengebirge": (50.63, 7.18, 50.73, 7.28),          # Siebengebirge
    "rothaargebirge": (50.85, 8.30, 51.20, 8.70),         # Rothaargebirge
    "taunus": (50.15, 8.30, 50.35, 8.60),                 # Taunus
    "odenwald": (49.50, 8.70, 49.90, 9.20),               # Odenwald

    # Deutschland gesamt (SEHR groß!)
    "deutschland": (47.27, 5.87, 55.06, 15.04),           # Ganz Deutschland
}


def main():
    parser = argparse.ArgumentParser(
        description="OSM Tiles Downloader für offline GPS-Gerät"
    )

    parser.add_argument(
        "--region",
        help="Vordefinierte Region (köln, berlin, münchen, hamburg)"
    )

    parser.add_argument(
        "--bbox",
        help="Bounding Box: lat_min,lon_min,lat_max,lon_max"
    )

    parser.add_argument(
        "--center",
        help="Center + Radius: lat,lon,radius_km"
    )

    parser.add_argument(
        "--zoom",
        default="12-16",
        help="Zoom-Level Bereich (z.B. 12-16, default: 12-16)"
    )

    parser.add_argument(
        "--output",
        default="data/maps",
        help="Output-Verzeichnis (default: data/maps)"
    )

    args = parser.parse_args()

    # Parse Zoom
    if '-' in args.zoom:
        zoom_min, zoom_max = map(int, args.zoom.split('-'))
    else:
        zoom_min = zoom_max = int(args.zoom)

    # Parse Region
    if args.region:
        region_name = args.region.lower()
        if region_name not in REGIONS:
            print(f"Fehler: Unbekannte Region '{args.region}'")
            print(f"Verfügbar: {', '.join(REGIONS.keys())}")
            sys.exit(1)

        lat_min, lon_min, lat_max, lon_max = REGIONS[region_name]
        print(f"Region: {args.region}")

    elif args.bbox:
        coords = list(map(float, args.bbox.split(',')))
        if len(coords) != 4:
            print("Fehler: Bbox muss 4 Werte haben: lat_min,lon_min,lat_max,lon_max")
            sys.exit(1)
        lat_min, lon_min, lat_max, lon_max = coords

    elif args.center:
        parts = args.center.split(',')
        if len(parts) != 3:
            print("Fehler: Center muss 3 Werte haben: lat,lon,radius_km")
            sys.exit(1)

        lat, lon, radius_km = map(float, parts)

        # Umrechnung km → Grad (grob)
        lat_delta = radius_km / 111.0  # 1° ≈ 111 km
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

        lat_min = lat - lat_delta
        lat_max = lat + lat_delta
        lon_min = lon - lon_delta
        lon_max = lon + lon_delta

        print(f"Center: {lat:.4f}, {lon:.4f} (Radius: {radius_km} km)")

    else:
        print("Fehler: --region, --bbox oder --center muss angegeben werden")
        parser.print_help()
        sys.exit(1)

    # Warnung bei großen Downloads
    tiles_estimate = 0
    for zoom in range(zoom_min, zoom_max + 1):
        x_min, y_max = OSMTileDownloader().lat_lon_to_tile(lat_min, lon_min, zoom)
        x_max, y_min = OSMTileDownloader().lat_lon_to_tile(lat_max, lon_max, zoom)
        tiles_estimate += (x_max - x_min + 1) * (y_max - y_min + 1)

    size_estimate_mb = tiles_estimate * 15 / 1024  # ~15 KB pro Tile

    print()
    print("=" * 50)
    print("WARNUNG: OSM Tile Usage Policy beachten!")
    print("=" * 50)
    print("- Max. 250.000 Tiles pro Tag")
    print("- User-Agent muss gesetzt sein")
    print("- Keine massenhaften Downloads")
    print("- Rate-Limit: ~10 Requests/Sekunde")
    print()
    print(f"Geschätzte Tiles: {tiles_estimate}")
    print(f"Geschätzter Speicher: {size_estimate_mb:.1f} MB")
    print(f"Geschätzte Zeit: {tiles_estimate * 0.1 / 60:.1f} Minuten")
    print()

    if tiles_estimate > 10000:
        response = input("Wirklich fortfahren? (ja/nein): ")
        if response.lower() not in ['ja', 'j', 'yes', 'y']:
            print("Abgebrochen.")
            sys.exit(0)

    # Download
    downloader = OSMTileDownloader(output_dir=args.output)
    downloader.download_region(lat_min, lon_min, lat_max, lon_max, zoom_min, zoom_max)


if __name__ == "__main__":
    main()
