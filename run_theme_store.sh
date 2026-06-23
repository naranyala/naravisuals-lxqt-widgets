#!/usr/bin/env bash
# NaraVisuals Theme Manager - Labwc/KWin/LXQt theming, panels, icons, fonts
cd "$(dirname "$0")"
echo "Launching nv-theme-store..."
PYTHONPATH=. python3 -m naravisuals.theme_manager.app
