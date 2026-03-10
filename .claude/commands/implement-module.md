---
description: Implementiere ein neues Hardware- oder Software-Modul
---

Implementiere ein Modul für das GPS-Projekt.

Benötigter Parameter: Modulname (z.B. "GPS", "IMU", "Navigation", "Display")

Schritte:

1. **Analyse:**
   - Prüfe CLAUDE.md für Spezifikationen
   - Checke relevante Agent-Dokumentation in `.claude/agents/`
   - Schaue ob bereits Basis-Code existiert

2. **Implementierung:**
   - Erstelle Modul-Datei in passendem `src/` Verzeichnis
   - Implementiere mit Mock-Unterstützung
   - Folge Code-Standards aus CLAUDE.md
   - Füge Type Hints hinzu
   - Schreibe deutsche Kommentare

3. **Tests:**
   - Erstelle Unit-Tests
   - Erstelle Mock-Tests
   - Falls Hardware: Erstelle Hardware-Test

4. **Dokumentation:**
   - Docstrings für alle Public-Methoden
   - Beispiel-Nutzung in Kommentaren

Nutze den passenden Agenten (hardware-agent, navigation-agent, display-agent).
