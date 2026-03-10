# Karten-Download Guide

Anleitung zum Herunterladen von OpenStreetMap-Karten für offline Nutzung.

---

## 🗺️ Verfügbare Regionen

### Städte (klein, ~20×20 km)
```bash
--region "köln"
--region "berlin"
--region "münchen"
--region "hamburg"
--region "frankfurt"
--region "düsseldorf"
```

**Speicherplatz:** ~30-50 MB (Zoom 12-16)
**Download-Zeit:** ~5-10 Minuten

---

### Regionen (mittel, ~100×100 km)
```bash
--region "rheinland"        # Rheinland
--region "ruhrgebiet"       # Ruhrgebiet
--region "bergisches-land"  # Bergisches Land
--region "eifel"            # Eifel
--region "sauerland"        # Sauerland
--region "schwarzwald"      # Schwarzwald
--region "harz"             # Harz
--region "allgäu"           # Allgäu
--region "bodensee"         # Bodensee
```

**Speicherplatz:** ~200-500 MB (Zoom 12-16)
**Download-Zeit:** ~30-60 Minuten

---

### Bundesländer (groß, ganze Regionen)
```bash
--region "nrw"              # NRW komplett (~400×250 km)
--region "bayern"           # Bayern komplett
--region "baden-württemberg"
--region "hessen"
--region "niedersachsen"
```

**Speicherplatz:** ~2-8 GB (Zoom 12-16)
**Download-Zeit:** 3-12 Stunden

---

### Wander-Gebiete (klein, präzise)
```bash
--region "siebengebirge"    # Siebengebirge
--region "rothaargebirge"   # Rothaargebirge
--region "taunus"           # Taunus
--region "odenwald"         # Odenwald
```

**Speicherplatz:** ~20-100 MB (Zoom 12-16)
**Download-Zeit:** ~5-20 Minuten

---

### Ganz Deutschland 🇩🇪
```bash
--region "deutschland"      # WARNUNG: SEHR GROSS!
```

**Speicherplatz:** ~30-50 GB (Zoom 12-16) ⚠️
**Download-Zeit:** 2-3 Tage! ⚠️

**Achtung:**
- Verstößt eventuell gegen OSM Usage Policy
- Besser: Nur Regionen die du wirklich brauchst

---

## 📊 Speicherplatz-Übersicht

Mit **64GB SD-Karte:**

| Setup | Regionen | Zoom | Speicher | Was bleibt |
|-------|----------|------|----------|------------|
| **Minimal** | 1 Stadt | 12-16 | ~40 MB | 63.96 GB |
| **Regional** | 3-5 Regionen | 12-16 | ~1 GB | 63 GB |
| **Bundesland** | 1 Bundesland | 12-16 | ~5 GB | 59 GB |
| **Multi-Region** | 5-10 Regionen | 12-16 | ~3 GB | 61 GB |
| **Deutsch-Ost** | 10+ Bundesländer | 12-14 | ~15 GB | 49 GB |
| **Fast alles** | 15 Bundesländer | 12-14 | ~25 GB | 39 GB |

**Fazit:** Mit 64GB kannst du **mehrere Bundesländer** speichern! ✅

---

## 🎯 Zoom-Level erklärt

| Zoom | Sichtbereich | Nutzen | Beispiel |
|------|--------------|--------|----------|
| **10** | ~50 km | Überblick Region | Autobahn-Navigation |
| **12** | ~10 km | Stadt-Überblick | Stadtplanung |
| **14** | ~2.5 km | Navigation | ⭐ **Standard-Zoom** |
| **16** | ~600 m | Detail | Wandern, Fußweg |
| **18** | ~150 m | Sehr detailliert | Gebäude-genau |

**Empfehlung für GPS-Gerät:** **Zoom 12-16** (guter Kompromiss)

**Speicherplatz nach Zoom:**
```
Köln 20×20 km:
- Zoom 12:      ~2 MB
- Zoom 14:      ~12 MB
- Zoom 16:      ~180 MB
- Zoom 12-16:   ~200 MB

NRW komplett:
- Zoom 12:      ~50 MB
- Zoom 14:      ~800 MB
- Zoom 16:      ~12 GB
- Zoom 12-16:   ~13 GB
- Zoom 12-14:   ~1 GB    ← Empfohlen für große Regionen!
```

---

## 💡 Empfohlene Setups

### Setup 1: "Home Region" (Empfohlen für Start)
```bash
# Deine Stadt + Umgebung
python scripts/download_maps.py --region "köln" --zoom 12-16

# + Wander-Gebiete in der Nähe
python scripts/download_maps.py --region "siebengebirge" --zoom 12-16
python scripts/download_maps.py --region "bergisches-land" --zoom 12-16
```

**Speicher:** ~300 MB
**Perfekt für:** Alltag + Wochenend-Touren

---

### Setup 2: "Regional Explorer"
```bash
# Ganzes Bundesland (reduzierter Zoom)
python scripts/download_maps.py --region "nrw" --zoom 12-14

# Deine Stadt in hoher Auflösung
python scripts/download_maps.py --region "köln" --zoom 14-16
```

**Speicher:** ~1.5 GB
**Perfekt für:** Regionale Touren

---

### Setup 3: "Deutschland-Wanderer"
```bash
# Mehrere Wander-Regionen
python scripts/download_maps.py --region "schwarzwald" --zoom 12-16
python scripts/download_maps.py --region "allgäu" --zoom 12-16
python scripts/download_maps.py --region "harz" --zoom 12-16
python scripts/download_maps.py --region "eifel" --zoom 12-16
```

**Speicher:** ~2 GB
**Perfekt für:** Urlaubs-Touren in verschiedenen Regionen

---

### Setup 4: "Bundesland-Paket" (mit 64GB möglich!)
```bash
# Ganzes Bundesland in Detail
python scripts/download_maps.py --region "nrw" --zoom 12-16

# Oder mehrere Bundesländer (reduziert)
python scripts/download_maps.py --region "nrw" --zoom 12-14
python scripts/download_maps.py --region "hessen" --zoom 12-14
python scripts/download_maps.py --region "bayern" --zoom 12-14
```

**Speicher:** ~3-8 GB
**Perfekt für:** Viel-Reisende

---

## 🚀 Download-Beispiele

### Auf dem Raspberry Pi (empfohlen!)

**1. Per SSH verbinden:**
```bash
ssh pi@raspberrypi.local
cd ~/gps_device
```

**2. Dependencies installieren:**
```bash
venv/bin/pip install requests pillow
```

**3. Download starten:**
```bash
# Kleine Region (schnell zum Testen)
venv/bin/python scripts/download_maps.py --region "siebengebirge" --zoom 12-16

# Deine Stadt
venv/bin/python scripts/download_maps.py --region "köln" --zoom 12-16

# Ganzes Bundesland (läuft über Nacht)
nohup venv/bin/python scripts/download_maps.py --region "nrw" --zoom 12-14 &
```

**4. Progress checken:**
```bash
# Bei nohup (Hintergrund):
tail -f nohup.out

# Speicherplatz prüfen:
du -sh data/maps/
```

---

### Eigene Bereiche definieren

**Bounding Box (Lat/Lon):**
```bash
# Beispiel: Eigenes Wander-Gebiet
python scripts/download_maps.py \
  --bbox 50.7,7.1,50.9,7.4 \
  --zoom 12-16
```

**Center + Radius:**
```bash
# 20 km Radius um dein Zuhause
python scripts/download_maps.py \
  --center 50.85,7.0,20 \
  --zoom 12-16
```

---

## ⏱️ Download-Zeiten (Beispiele)

**Auf Raspberry Pi Zero 2 W (WLAN):**

| Region | Zoom | Tiles | Zeit | Speicher |
|--------|------|-------|------|----------|
| Siebengebirge | 12-16 | ~1.200 | 2 Min | 18 MB |
| Köln | 12-16 | ~2.800 | 5 Min | 42 MB |
| Ruhrgebiet | 12-16 | ~18.000 | 30 Min | 270 MB |
| NRW | 12-14 | ~65.000 | 2 Std | 980 MB |
| NRW | 12-16 | ~850.000 | 24 Std | 13 GB |
| Deutschland | 12-14 | ~2 Mio | 3 Tage | 30 GB |

**Mit LAN (schneller):** ~30% weniger Zeit

---

## 🛡️ OSM Usage Policy beachten!

**Wichtige Regeln:**
1. ✅ Max. **250.000 Tiles pro Tag** (automatisch begrenzt im Skript)
2. ✅ **User-Agent** muss gesetzt sein (ist im Skript drin)
3. ✅ **Rate-Limit** 10 Requests/Sekunde (im Skript: 0.1s Delay)
4. ❌ **Keine massenhaften Downloads** ohne Grund
5. ✅ **Tile-Server respektieren** (OpenStreetMap ist kostenlos!)

**Was ist OK:**
- Deine Region für persönliche Nutzung ✅
- Mehrere Bundesländer für Urlaube ✅
- Update alle paar Monate ✅

**Was ist NICHT OK:**
- Ganz Europa auf einmal ❌
- Täglich neu downloaden ❌
- Für kommerzielle Projekte ohne Lizenz ❌

---

## 🔧 Karten aktualisieren

**OSM-Daten ändern sich:**
- Neue Straßen, Wege, Gebäude
- POIs (Restaurants, etc.)
- Empfehlung: **Update alle 3-6 Monate**

**Update-Befehl:**
```bash
# Alte Karten löschen
rm -rf data/maps/tiles

# Neu downloaden
python scripts/download_maps.py --region "köln" --zoom 12-16
```

**Oder:** Nur geänderte Tiles (TODO: Feature für später)

---

## 📱 Karten-Verwaltung

### Welche Regionen habe ich?
```bash
# Metadata prüfen
cat data/maps/metadata.json

# Speicherplatz
du -sh data/maps/
du -h data/maps/tiles/*/
```

### Einzelne Regionen löschen
```bash
# Zoom 16 löschen (spart Platz)
rm -rf data/maps/tiles/16

# Nur bestimmte Region behalten
# → Download neu mit anderem output-Pfad
```

---

## 🎯 Empfehlung für dich

**Starter-Setup (500 MB):**
```bash
# 1. Deine Heimat-Stadt
python scripts/download_maps.py --region "köln" --zoom 12-16

# 2. Beliebte Wander-Ziele
python scripts/download_maps.py --region "siebengebirge" --zoom 12-16
python scripts/download_maps.py --region "eifel" --zoom 12-16
```

**Später erweitern:**
```bash
# Urlaubs-Regionen hinzufügen
python scripts/download_maps.py --region "schwarzwald" --zoom 12-16
python scripts/download_maps.py --region "allgäu" --zoom 12-16
```

**Ultimate-Setup (10 GB):**
```bash
# Ganzes Bundesland
python scripts/download_maps.py --region "nrw" --zoom 12-14

# Wichtige Städte hochauflösend
python scripts/download_maps.py --region "köln" --zoom 14-16
python scripts/download_maps.py --region "düsseldorf" --zoom 14-16

# Wander-Gebiete komplett
python scripts/download_maps.py --region "eifel" --zoom 12-16
python scripts/download_maps.py --region "sauerland" --zoom 12-16
```

---

## ⚠️ Troubleshooting

### "HTTP 429 - Too Many Requests"
→ Du downloadst zu schnell
→ **Lösung:** Warte 1 Stunde, dann weiter

### "Connection timeout"
→ Netzwerk-Problem
→ **Lösung:** WLAN prüfen, Script neu starten (überspringt vorhandene Tiles)

### "Disk full"
→ SD-Karte voll
→ **Lösung:** `df -h` prüfen, alte Logs löschen

### Download dauert ewig
→ Raspberry Pi ist langsam
→ **Lösung:**
  - Auf deinem PC downloaden → dann per SCP auf Pi kopieren
  - Oder: Über Nacht laufen lassen

---

## 💾 Speicher-Tipps

**Mit 64GB kannst du:**
- ✅ 5-10 Bundesländer (Zoom 12-14)
- ✅ 20-30 Städte (Zoom 12-16)
- ✅ 50+ Wander-Gebiete (Zoom 12-16)
- ✅ Deine ganze Region hochauflösend

**Speicher sparen:**
```bash
# Nur Zoom 12-14 statt 12-16 (spart 90%!)
--zoom 12-14

# Nur wichtige Bereiche hochauflösend
--region "köln" --zoom 14-16      # Detail
--region "nrw" --zoom 12-13       # Übersicht
```

**Was brauchst du wirklich?**
- **Zoom 12-13:** Überblick, Autofahren
- **Zoom 14:** ⭐ **Standard**, Wandern, Radfahren
- **Zoom 15-16:** Detail, Stadtplan, Fußwege

→ **Zoom 12-14 reicht meistens!** Spart 80% Speicher.

---

## 🌍 Alternative Tile-Server (später)

**Standard:** OpenStreetMap (kostenlos)
```
https://tile.openstreetmap.org/{z}/{x}/{y}.png
```

**Alternative (wenn OSM überlastet):**
- OpenTopoMap (topografisch): `https://tile.opentopomap.org/`
- CyclOSM (Fahrrad): `https://tile.cyclosm.openstreetmap.fr/`
- Humanitarian (humanitär): `https://tile.openstreetmap.fr/hot/`

**Im Skript ändern:**
```python
self.tile_server = "https://tile.opentopomap.org"
```

---

**Stand:** 2024-03-09
**Skript:** `scripts/download_maps.py`
**Verfügbare Regionen:** 30+
