"""Pytest configuration for NaraVisuals tests."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set test environment
os.environ["QT_QPA_PLATFORM"] = "offscreen"
