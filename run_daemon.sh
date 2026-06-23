#!/usr/bin/env bash
# NaraVisuals D-Bus Daemon
cd "$(dirname "$0")"
echo "Launching nv-daemon..."
PYTHONPATH=. python3 -m naravisuals.daemon.__main__
