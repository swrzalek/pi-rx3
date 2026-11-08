#!/usr/bin/env python3
"""Create a separate RX3 v1.19 candidate with BiteDJ's fourth tempo range.
Requires matching native-tempo25 artwork support in the runtime shim.
Never overwrite the input executable or patch a running process.
"""

import argparse, struct
from pathlib import Path


def patched(data):
    b = bytearray(data)
    if b[:7] != b"\x7fELF\x01\x01\x01":
        raise ValueError("Expected little-endian ELF32")
    changes = (
        (0x41C8E0, struct.pack("<iid", 100, 50, 0.02), struct.pack("<iid", 25, 5, 0.2)),
        (0x4D3C20, struct.pack("<4I", 6, 10, 16, 100), struct.pack("<4I", 6, 10, 16, 25)),
        (0x122B04, struct.pack("<I", 0xE3500064), struct.pack("<I", 0xE3500019)),
        # Keep the original 25% label slot but use hundredths tempo layout.
        (0x28A438, struct.pack("<I", 0x01A0A000), struct.pack("<I", 0x03A0A000)),
        (0x28A450, struct.pack("<I", 0xE1A0A001), struct.pack("<I", 0xE3A0A000)),
    )
    # These addresses all lie in the first executable LOAD segment.
    phoff = struct.unpack_from("<I", b, 28)[0]
    entsize, count = struct.unpack_from("<HH", b, 42)
    segments = [struct.unpack_from("<8I", b, phoff + i * entsize) for i in range(count)]
    edits = []
    for addr, old, new in changes:
        seg = next(
            (s for s in segments if s[0] == 1 and s[2] <= addr and addr + len(old) <= s[2] + s[4]),
            None,
        )
        if seg is None:
            raise ValueError(f"Unmapped patch address {addr:#x}")
        offset = seg[1] + addr - seg[2]
        if b[offset : offset + len(old)] != old:
            raise ValueError(f"Native bytes differ at {addr:#x}")
        edits.append((offset, new))
    for offset, new in edits:
        b[offset : offset + len(new)] = new
    return bytes(b)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    if a.input.resolve() == a.output.resolve():
        ap.error("Use a separate output file")
    result = patched(a.input.read_bytes())
    with a.output.open("xb") as out:
        out.write(result)
    a.output.chmod(a.input.stat().st_mode & 0o777)
    print("Created 25% candidate; deploy with matching artwork shim after stopping RX3")
