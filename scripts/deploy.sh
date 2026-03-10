#!/bin/bash
# Deploy-Skript - Kopiert Projekt auf Raspberry Pi

set -e

# Konfiguration
PI_USER="pi"
PI_HOST="raspberrypi.local"
PI_DIR="/home/pi/gps_device"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== GPS-Gerät Deployment ===${NC}"
echo ""

# Prüfe ob SSH-Verbindung funktioniert
echo -e "${YELLOW}Prüfe SSH-Verbindung zu ${PI_USER}@${PI_HOST}...${NC}"
if ! ssh -o ConnectTimeout=5 ${PI_USER}@${PI_HOST} "echo 'Verbindung OK'" > /dev/null 2>&1; then
    echo -e "${RED}Fehler: Keine Verbindung zum Raspberry Pi${NC}"
    echo "Prüfe:"
    echo "  - Ist der Pi eingeschaltet?"
    echo "  - Ist er im gleichen Netzwerk?"
    echo "  - Funktioniert SSH? (ssh ${PI_USER}@${PI_HOST})"
    exit 1
fi
echo -e "${GREEN}✓ SSH-Verbindung erfolgreich${NC}"

# Erstelle Deployment-Paket (ohne unnötige Dateien)
echo -e "${YELLOW}Erstelle Deployment-Paket...${NC}"
TEMP_DIR=$(mktemp -d)
rsync -av --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='data' \
    --exclude='.env' \
    --exclude='htmlcov' \
    --exclude='.pytest_cache' \
    ./ ${TEMP_DIR}/

echo -e "${GREEN}✓ Deployment-Paket erstellt${NC}"

# Übertrage auf Pi
echo -e "${YELLOW}Übertrage Dateien auf Raspberry Pi...${NC}"
rsync -av --progress \
    ${TEMP_DIR}/ \
    ${PI_USER}@${PI_HOST}:${PI_DIR}/

echo -e "${GREEN}✓ Dateien übertragen${NC}"

# Cleanup
rm -rf ${TEMP_DIR}

# Installiere Dependencies auf Pi
echo -e "${YELLOW}Installiere Python-Dependencies auf Pi...${NC}"
ssh ${PI_USER}@${PI_HOST} "cd ${PI_DIR} && venv/bin/pip install -r requirements.txt"
echo -e "${GREEN}✓ Dependencies installiert${NC}"

# Setze Berechtigungen
echo -e "${YELLOW}Setze Berechtigungen...${NC}"
ssh ${PI_USER}@${PI_HOST} "chmod +x ${PI_DIR}/src/main.py"
echo -e "${GREEN}✓ Berechtigungen gesetzt${NC}"

echo ""
echo -e "${GREEN}=== Deployment abgeschlossen! ===${NC}"
echo ""
echo -e "${YELLOW}Nächste Schritte:${NC}"
echo "1. Programm testen: ${GREEN}ssh ${PI_USER}@${PI_HOST} 'cd ${PI_DIR} && venv/bin/python3 src/main.py'${NC}"
echo "2. Service neu starten: ${GREEN}ssh ${PI_USER}@${PI_HOST} 'sudo systemctl restart gps-device'${NC}"
echo "3. Logs ansehen: ${GREEN}ssh ${PI_USER}@${PI_HOST} 'sudo journalctl -u gps-device -f'${NC}"
echo ""
