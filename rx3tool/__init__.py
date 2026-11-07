"""Setup, validation and launch helpers for running the RX3 player on a Pi.

Standard library only, so the tool works before any Python package is
installed. Firmware decryption additionally needs `cryptography`.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
