#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="${PREFIX}/bin"
LIB_DIR="${PREFIX}/lib/naravisuals"
APP_DIR="${PREFIX}/share/applications"
PANEL_PLUGIN_DIR="${PREFIX}/share/lxqt/lxqt-panel"
SERVICE_DIR="${PREFIX}/share/systemd/user"
DBUS_DIR="${PREFIX}/share/dbus-1/services"
AUTOSTART_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"

# Detect distribution type
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID="${ID}"
        DISTRO_LIKE="${ID_LIKE:-}"
    elif [ -f /etc/redhat-release ]; then
        DISTRO_ID="rhel"
        DISTRO_LIKE="rhel fedora"
    elif [ -f /etc/debian_version ]; then
        DISTRO_ID="debian"
        DISTRO_LIKE="debian"
    else
        DISTRO_ID="unknown"
        DISTRO_LIKE=""
    fi
    
    # Check if RPM-based
    if [[ "$DISTRO_LIKE" =~ (rhel|fedora|rhel-fedora) ]] || [[ "$DISTRO_ID" =~ (fedora|rhel|centos|rocky|alma|ol) ]]; then
        PKG_MANAGER="rpm"
    elif [[ "$DISTRO_LIKE" =~ (debian|ubuntu) ]] || [[ "$DISTRO_ID" =~ (debian|ubuntu|linuxmint|pop|elementary) ]]; then
        PKG_MANAGER="deb"
    elif [[ "$DISTRO_ID" =~ (arch|manjaro|endeavouros|garuda) ]]; then
        PKG_MANAGER="pacman"
    else
        PKG_MANAGER="unknown"
    fi
}

detect_distro

echo "==> Installing NaraVisuals LXQt Widgets (D-Bus architecture)..."
echo "    Detected: $DISTRO_ID ($PKG_MANAGER-based)"
echo ""

mkdir -p "$BIN_DIR" "$LIB_DIR" "$APP_DIR" "$PANEL_PLUGIN_DIR" "$SERVICE_DIR" "$DBUS_DIR" "$AUTOSTART_DIR"

# Install Python packages
cp -r "$PROJECT_DIR/naravisuals" "$LIB_DIR/"

# Create launcher scripts
cat > "$BIN_DIR/naravisuals-manager" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.manager.control_center "$@"
SCRIPT
chmod +x "$BIN_DIR/naravisuals-manager"

cat > "$BIN_DIR/naravisuals-manager-legacy" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.manager.app "$@"
SCRIPT
chmod +x "$BIN_DIR/naravisuals-manager-legacy"

cat > "$BIN_DIR/naravisuals-daemon" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.daemon "$@"
SCRIPT
chmod +x "$BIN_DIR/naravisuals-daemon"

# Install systemd user service
cp "$PROJECT_DIR/packaging/naravisuals-daemon.service" "$SERVICE_DIR/"

# Install D-Bus service file
cat > "$DBUS_DIR/org.naravisuals.Daemon.service" << DBUS
[D-BUS Service]
Name=org.naravisuals.Daemon
Exec=${BIN_DIR}/naravisuals-daemon
User=${USER}
DBUS_SERVICE=org.naravisuals.Daemon
DBUS_PATH=/org/naravisuals/Daemon
DBUS_INTERFACE=org.naravisuals.Daemon
DBUS_ACTIVATABLE=true
DBUS_BUS_TYPE=session
DBUS_DESCRIPTION=NaraVisuals LXQt Widgets Daemon
DBUS_NAME=org.naravisuals.Daemon
DBUS_OBJECT=/org/naravisuals/Daemon
DBUS_TYPE=method_call
DBUS_INTERFACE_NAME=org.naravisuals.Daemon
DBUS_METHOD=GetData
DBUS_SIGNATURE=s
DBUS_ENABLED=true
DBUS_USER=${USER}
DBUS_SYSTEM=false
DBUS_SESSION=true
DBUS_SYSTEMD_SERVICE=naravisuals-daemon.service
DBUS_XDG_AUTOSTART=true
DBUS_XDG_AUTOSTART_DIR=${AUTOSTART_DIR}
DBUS_VERSION=1.0
DBUS_PROTOCOL_VERSION=1
DBUS_MAX_ARGS=255
DBUS_MAX_ARRAY_NESTING=10
DBUS_MAX_STRUCT_NESTING=20
DBUS_MAX_UNIX_FDS=16
DBUS_MAX_MATCH_RULE_LENGTH=1024
DBUS_MAX_SERVICE_NAME_LENGTH=255
DBUS_MAX_OBJECT_PATH_LENGTH=255
DBUS_MAX_INTERFACE_NAME_LENGTH=255
DBUS_MAX_MEMBER_NAME_LENGTH=255
DBUS_MAX_ERROR_NAME_LENGTH=255
DBUS_MAX_ENVIRONMENT_VARIABLE_LENGTH=4095
DBUS_MAX_ARRAY_LENGTH=67108864
DBUS_MAX_BYTE_ARRAY_LENGTH=67108864
DBUS_MAX_STRING_LENGTH=134217727
DBUS_MAX_SIGNATURE_LENGTH=255
DBUS_MAX_CONNECTION_DATA_LENGTH=134217727
DBUS_MAX_MATCH_RULE_LENGTH=1024
DBUS_MAX_NAME_LENGTH=255
DBUS_MAX_PATH_LENGTH=255
DBUS_MAX_INTERFACE_LENGTH=255
DBUS_MAX_MEMBER_LENGTH=255
DBUS_MAX_ERROR_LENGTH=255
DBUS_MAX_ENVIRONMENT_LENGTH=4095
DBUS_MAX_ARRAY_LENGTH=67108864
DBUS_MAX_BYTE_ARRAY_LENGTH=67108864
DBUS_MAX_STRING_LENGTH=134217727
DBUS_MAX_SIGNATURE_LENGTH=255
DBUS_MAX_CONNECTION_DATA_LENGTH=134217727
DBUS
chmod 644 "$DBUS_DIR/org.naravisuals.Daemon.service"

# Install desktop files
for f in "$PROJECT_DIR/desktop/naravisuals-"*.desktop; do
    name=$(basename "$f")
    cp "$f" "$APP_DIR/$name"
done

# Install panel reset tool
cp "$PROJECT_DIR/scripts/naravisuals-panel-reset" "$BIN_DIR/"
chmod +x "$BIN_DIR/naravisuals-panel-reset"

# Install stock panel config
mkdir -p "$PREFIX/share/naravisuals"
cp "$PROJECT_DIR/packaging/stock-panel.conf" "$PREFIX/share/naravisuals/"

# Create autostart entry for daemon
cat > "$AUTOSTART_DIR/naravisuals-daemon.desktop" << AUTOSTART
[Desktop Entry]
Type=Application
Name=NaraVisuals Daemon
Exec=${BIN_DIR}/naravisuals-daemon
Terminal=false
X-LXQt-Needs=Panel
AUTOSTART

echo "  Launcher scripts:  $BIN_DIR"
echo "  Python packages:   $LIB_DIR"
echo "  Desktop files:     $APP_DIR"
echo "  Systemd service:   $SERVICE_DIR"
echo "  D-Bus service:     $DBUS_DIR"
echo "  Autostart:         $AUTOSTART_DIR"
echo ""

# Check and install missing dependencies based on package manager
check_dependencies() {
    local missing=()
    
    case $PKG_MANAGER in
        rpm)
            echo "==> Checking RPM dependencies..."
            for pkg in python3 python3-pyqt6 python3-psutil python3-requests python3-dbus-python; do
                if ! rpm -q "$pkg" &>/dev/null; then
                    missing+=("$pkg")
                fi
            done
            if [ ${#missing[@]} -gt 0 ]; then
                echo "  Missing packages: ${missing[*]}"
                echo "  Install with: sudo dnf install ${missing[*]}"
                echo ""
            fi
            ;;
        deb)
            echo "==> Checking DEB dependencies..."
            for pkg in python3 python3-pyqt6 python3-psutil python3-requests python3-dbus-python; do
                if ! dpkg -l "$pkg" &>/dev/null; then
                    missing+=("$pkg")
                fi
            done
            if [ ${#missing[@]} -gt 0 ]; then
                echo "  Missing packages: ${missing[*]}"
                echo "  Install with: sudo apt install ${missing[*]}"
                echo ""
            fi
            ;;
        pacman)
            echo "==> Checking Pacman dependencies..."
            for pkg in python python-pyqt6 python-psutil python-requests python-dbus python-notify2; do
                if ! pacman -Qi "$pkg" &>/dev/null; then
                    missing+=("$pkg")
                fi
            done
            if [ ${#missing[@]} -gt 0 ]; then
                echo "  Missing packages: ${missing[*]}"
                echo "  Install with: sudo pacman -S ${missing[*]}"
                echo ""
            fi
            ;;
    esac
}

check_dependencies

# Enable systemd service
if command -v systemctl &> /dev/null; then
    echo "==> Enabling systemd user service..."
    systemctl --user daemon-reload
    systemctl --user enable naravisuals-daemon.service
    echo "  Service enabled (will start on next login)"
    echo "  To start now: systemctl --user start naravisuals-daemon"
fi

echo ""
echo "==> Updating desktop database..."
update-desktop-database "$APP_DIR" 2>/dev/null || true

echo ""
echo "==> Installation complete!"
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  NaraVisuals LXQt Widgets (D-Bus Architecture)"
echo ""
echo "  ARCHITECTURE:"
echo "    naravisuals-daemon  - Background D-Bus service (auto-started)"
echo "    naravisuals-manager - Widget configuration GUI"
echo ""
echo "  TO ADD TO PANEL (LXQt GUI method):"
echo "  1. Right-click on the LXQt panel > 'Add Widgets...'"
echo "  2. Look for 'NaraVisuals' entries in the list"
echo ""
echo "  STANDALONE LAUNCH:"
echo "    naravisuals-manager           - Widget manager"
echo "    naravisuals-daemon            - D-Bus daemon (usually auto-started)"
echo ""
echo "  MANUAL DAEMON CONTROL:"
echo "    systemctl --user start naravisuals-daemon"
echo "    systemctl --user stop naravisuals-daemon"
echo "    systemctl --user status naravisuals-daemon"
echo ""
echo "  PANEL MANAGEMENT:"
echo "    naravisuals-panel-reset --stock       Reset panel to stock config"
echo "    naravisuals-panel-reset --backup      Restore from last backup"
echo "    naravisuals-panel-reset --dry-run     Preview changes without applying"
echo ""
echo "  REMOVE:"
echo "    systemctl --user stop naravisuals-daemon"
echo "    systemctl --user disable naravisuals-daemon"
echo "    naravisuals-panel-reset --stock       Reset panel first"
echo "    rm -rf $LIB_DIR $BIN_DIR/naravisuals-*"
echo "──────────────────────────────────────────────────────────────"
