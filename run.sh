#!/usr/bin/env bash

# Navigate to the directory where the script is located
cd "$(dirname "$0")"

# Launch the NaraVisuals Settings Hub GUI
echo "🚀 Launching NaraVisuals Settings Hub..."
PYTHONPATH=. python3 -m naravisuals.manager.app
