#!/usr/bin/env python3
"""Compatibility name for ./rx3 recover (recover RX3 1.19 from official downloads).

Outputs now go to work/firmware/ (see ./rx3 recover --help); nothing is flashed.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rx3tool.cli import main  # noqa: E402

if __name__ == '__main__':
    sys.exit(main(['recover'] + sys.argv[1:]))
