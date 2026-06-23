#!/usr/bin/env bash
# NaraVisuals Settings Hub - Widget config & panel organizer
cd "$(dirname "$0")"
echo "Launching nv-manager-legacy..."
PYTHONPATH=. python3 -m naravisuals.manager.app
