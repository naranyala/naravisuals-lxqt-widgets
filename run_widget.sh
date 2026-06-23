#!/usr/bin/env bash
# NaraVisuals Widget Runner
cd "$(dirname "$0")"
echo "Launching nv-widget..."
PYTHONPATH=. python3 -m naravisuals.widgets.__main__
