#!/usr/bin/env bash
# NaraVisuals SDDM Login Manager
cd "$(dirname "$0")"
echo "Launching nv-sddm-manager..."
PYTHONPATH=. python3 -m naravisuals.sddm_manager.app
