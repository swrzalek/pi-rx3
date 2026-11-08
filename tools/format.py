#!/usr/bin/env python3
"""Format tracked Python/C sources, or check them with --check."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report changes without writing files")
    args = parser.parse_args()
    # Use tools from this Python environment even when its bin directory is not on PATH.
    binaries = {}
    for name in ("ruff", "clang-format"):
        local = Path(sys.executable).parent / name
        binaries[name] = str(local) if local.is_file() else shutil.which(name)
        if not binaries[name]:
            parser.error(f"Missing {name}; run: python3 -m pip install -r requirements-dev.txt")
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    files = sorted(set(result.stdout.decode().rstrip("\0").split("\0")))
    files = [f for f in files if (ROOT / f).is_file()]
    python = [f for f in files if f.endswith(".py") or f == "rx3"]
    native = [f for f in files if f.endswith((".c", ".h")) and not f.endswith("-glyphs.h")]
    commands = [
        [binaries["ruff"], "format"] + (["--check"] if args.check else []) + python,
        [binaries["clang-format"], "--style=file"]
        + (["--dry-run", "--Werror"] if args.check else ["-i"])
        + native,
    ]
    failed = False
    for command in commands:
        if subprocess.run(command, cwd=ROOT).returncode:
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
