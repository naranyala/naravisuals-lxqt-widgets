#!/usr/bin/env bash
# NaraVisuals Control Center - All-in-one GUI
cd "$(dirname "$0")"
echo "Launching nv-manager..."
PYTHONPATH=. python3 -m naravisuals.manager.control_center
