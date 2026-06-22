#!/usr/bin/env bash
set -e

PLUGIN_DIR="/usr/lib/x86_64-linux-gnu/lxqt-panel"
DESKTOP_DIR="/usr/share/lxqt/lxqt-panel"
NATIVE_BUILD="/media/naranyala/Data/projects-remote/naravisuals-lxqt-widgets/native-plugin/build"

echo "==> Installing NaraVisuals native LXQt panel plugin..."
echo ""

# Install the main .so
cp "$NATIVE_BUILD/libnaravisuals.so" "$PLUGIN_DIR/libnaravisuals.so"
chmod 755 "$PLUGIN_DIR/libnaravisuals.so"

# Create symlinks for each widget variant
for widget in system-monitor weather quick-notes clipboard-manager pomodoro network-monitor tray-enhanced media-player battery; do
    ln -sf libnaravisuals.so "$PLUGIN_DIR/libnaravisuals-${widget}.so"
done

echo "  Plugin installed: $PLUGIN_DIR/libnaravisuals.so"
echo "  Symlinks: libnaravisuals-{widget}.so -> libnaravisuals.so"

# Install .desktop files
for f in /media/naranyala/Data/projects-remote/naravisuals-lxqt-widgets/desktop-panel/naravisuals-*.desktop; do
    cp "$f" "$DESKTOP_DIR/"
    echo "  Desktop: $DESKTOP_DIR/$(basename $f)"
done

echo ""
echo "==> Plugin installation complete!"
echo ""
echo "Now restart the panel:"
echo "  lxqt-panel --replace &"
echo ""
echo "Then right-click panel → Add Widgets..."
echo "Look for: System Monitor, Weather, Network Monitor, etc."
