#!/bin/bash
# Setup-Skript für Raspberry Pi Zero 2 W
# Installiert alle Dependencies und konfiguriert das System

set -e  # Beende bei Fehler

echo "=== GPS-Gerät Setup für Raspberry Pi Zero 2 W ==="
echo ""

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prüfe ob als root ausgeführt
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Bitte als root ausführen (sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}[1/9] System aktualisieren...${NC}"
apt update
apt upgrade -y

echo -e "${GREEN}[2/9] Python 3 und pip installieren...${NC}"
apt install -y python3 python3-pip python3-venv git

echo -e "${GREEN}[3/9] System-Bibliotheken installieren...${NC}"
apt install -y \
    i2c-tools \
    python3-smbus \
    python3-rpi.gpio \
    python3-pil \
    python3-numpy \
    gpsd gpsd-clients python3-gps

echo -e "${GREEN}[4/9] Interfaces aktivieren (I2C, SPI, UART)...${NC}"

# I2C aktivieren
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
    echo "  ✓ I2C aktiviert"
fi

# SPI aktivieren
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" >> /boot/config.txt
    echo "  ✓ SPI aktiviert"
fi

# UART aktivieren (für GPS)
if ! grep -q "^enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" >> /boot/config.txt
    echo "  ✓ UART aktiviert"
fi

# Serial Console deaktivieren (wichtig für GPS!)
if systemctl is-enabled serial-getty@ttyS0.service > /dev/null 2>&1; then
    systemctl disable serial-getty@ttyS0.service
    echo "  ✓ Serial Console deaktiviert"
fi

# Entferne console=serial0 aus cmdline.txt
sed -i 's/console=serial0,[0-9]\+ //' /boot/cmdline.txt

echo -e "${GREEN}[5/9] Waveshare ePaper Library installieren...${NC}"
cd /tmp
if [ ! -d "e-Paper" ]; then
    git clone https://github.com/waveshare/e-Paper.git
fi
cd e-Paper/RaspberryPi_JetsonNano/python
pip3 install .
cd ~

echo -e "${GREEN}[6/9] GPS-Daemon konfigurieren...${NC}"

# GPSD-Konfiguration
cat > /etc/default/gpsd <<EOF
# GPS-Daemon Konfiguration für NEO-M8N
START_DAEMON="true"
GPSD_OPTIONS="-n"
DEVICES="/dev/ttyS0"
USBAUTO="false"
GPSD_SOCKET="/var/run/gpsd.sock"
EOF

# GPSD neu starten
systemctl enable gpsd
systemctl restart gpsd

echo "  ✓ GPSD konfiguriert"

echo -e "${GREEN}[7/9] Projekt-Verzeichnis erstellen...${NC}"

PROJECT_DIR="/home/pi/gps_device"
mkdir -p $PROJECT_DIR
chown -R pi:pi $PROJECT_DIR

echo "  ✓ Projekt-Verzeichnis: $PROJECT_DIR"

echo -e "${GREEN}[8/9] Python Virtual Environment erstellen...${NC}"

cd $PROJECT_DIR
sudo -u pi python3 -m venv venv
sudo -u pi $PROJECT_DIR/venv/bin/pip install --upgrade pip

echo "  ✓ Virtual Environment erstellt"

echo -e "${GREEN}[9/9] Systemd Service erstellen...${NC}"

cat > /etc/systemd/system/gps-device.service <<EOF
[Unit]
Description=DIY GPS Outdoor Device
After=network.target gpsd.service
Wants=gpsd.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/gps_device
ExecStart=/home/pi/gps_device/venv/bin/python3 src/main.py
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "  ✓ Systemd Service erstellt (gps-device.service)"

echo ""
echo -e "${GREEN}=== Setup abgeschlossen! ===${NC}"
echo ""
echo -e "${YELLOW}Nächste Schritte:${NC}"
echo "1. Raspberry Pi neu starten: ${GREEN}sudo reboot${NC}"
echo "2. Projekt-Code in $PROJECT_DIR kopieren"
echo "3. Dependencies installieren: ${GREEN}venv/bin/pip install -r requirements.txt${NC}"
echo "4. Service aktivieren: ${GREEN}sudo systemctl enable gps-device${NC}"
echo "5. Service starten: ${GREEN}sudo systemctl start gps-device${NC}"
echo ""
echo -e "${YELLOW}Hardware testen:${NC}"
echo "- I2C: ${GREEN}i2cdetect -y 1${NC}"
echo "- GPS: ${GREEN}cgps -s${NC}"
echo "- SPI: ${GREEN}ls /dev/spidev*${NC}"
echo ""
echo -e "${RED}WICHTIG: Reboot erforderlich für Interface-Aktivierung!${NC}"
