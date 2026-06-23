#!/usr/bin/env bash
# NaraVisuals Desktop Manager - Manage .desktop files across the system
cd "$(dirname "$0")"
echo "Launching nv-desktop-manager..."
PYTHONPATH=. python3 -m naravisuals.desktop_manager.app
