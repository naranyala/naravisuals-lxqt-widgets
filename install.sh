#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.local/share/applications"
PANEL_PLUGIN_DIR="${HOME}/.local/share/lxqt/lxqt-panel"
AUTOSTART_DIR="${HOME}/.config/autostart"

echo "==> Installing NaraVisuals LXQt Widgets..."
echo ""

mkdir -p "$BIN_DIR" "$APP_DIR" "$PANEL_PLUGIN_DIR" "$AUTOSTART_DIR"

cp -r "$PROJECT_DIR/naravisuals" "$BIN_DIR/"

cat > "$BIN_DIR/naravisuals-manager" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.panel_plugin "$@"
SCRIPT
chmod +x "$BIN_DIR/naravisuals-manager"

for widget in system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery; do
    name="naravisuals-${widget}"
    cat > "$BIN_DIR/$name" << SCRIPT
#!/usr/bin/env bash
exec python3 -m naravisuals.widgets ${widget} "\$@"
SCRIPT
    chmod +x "$BIN_DIR/$name"
done

for f in "$PROJECT_DIR/desktop/naravisuals-"*.desktop; do
    name=$(basename "$f")
    cp "$f" "$APP_DIR/$name"
done

echo "  Launcher scripts:  $BIN_DIR"
echo "  Desktop files:     $APP_DIR"
echo ""

echo "==> Creating autostart entries (launch with --panel mode)..."
for widget in system-monitor weather network-monitor battery; do
    name="naravisuals-${widget}"
    cat > "$AUTOSTART_DIR/${name}.desktop" << AUTOSTART
[Desktop Entry]
Type=Application
Name=NaraVisuals ${widget}
Exec=${name} --panel
Terminal=false
X-LXQt-Needs=Panel
AUTOSTART
    echo "  + Autostart: ${widget}"
done

echo ""
echo "==> Updating desktop database..."
update-desktop-database "$APP_DIR" 2>/dev/null || true

echo ""
echo "==> Installation complete!"
echo ""
echo "──────────────────────────────────────────────────────────────"
echo "  NaraVisuals LXQt Widgets are ready!"
echo ""
echo "  TO ADD TO PANEL (LXQt GUI method):"
echo "  1. Right-click on the LXQt panel → 'Add Widgets...'"
echo "  2. Or right-click → 'Panel Settings' → 'Widgets' tab"
echo "  3. Look for 'NaraVisuals' entries in the list"
echo ""
echo "  TO ADD VIA QUICK LAUNCH:"
echo "  1. Right-click panel → 'Add Widgets...' → 'Quick Launch'"
echo "  2. Right-click the Quick Launch area → 'Preferences'"
echo "  3. Click 'Add' and find NaraVisuals entries in the menu"
echo ""
echo "  STANDALONE LAUNCH:"
echo "    naravisuals-manager           - Widget manager"
echo "    naravisuals-system-monitor    - CPU/RAM/Disk/SWAP"
echo "    naravisuals-weather           - Weather info"
echo "    naravisuals-quick-notes       - Sticky notes"
echo "    naravisuals-clipboard-manager - Clipboard history"
echo "    naravisuals-pomodoro          - Timer"
echo "    naravisuals-network-monitor   - Traffic graph"
echo "    naravisuals-tray-enhanced     - Tray management"
echo "    naravisuals-media-player      - MPRIS control"
echo "    naravisuals-battery           - Battery status"
echo ""
echo "  PANEL MODE (frameless, always-on-top):"
echo "    naravisuals-weather --panel --position 1800+30 --width 200"
echo ""
echo "  REMOVE: naravisuals-remove"
echo "──────────────────────────────────────────────────────────────"
