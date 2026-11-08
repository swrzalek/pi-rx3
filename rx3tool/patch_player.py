#!/usr/bin/env python3
"""Create rbp-pi from the verified RX3 1.19 rbp and the ARM clock stub.

Usage: patch-player.py [ORIGINAL_RBP] [PI_CLOCK_BIN] [OUTPUT]
Defaults keep the original layout: pi-runtime/rbp, pi-clock.bin, rbp-pi.
`./rx3 install` calls patched() directly; the input is never modified.
"""

from pathlib import Path
import hashlib
import struct
import sys

PLAYER_SHA256 = "60bcbd8876116bf09f0d8f747f95d7c7d3081ebd39d6fe14d56005a22f7f3b09"
# The stub replaces user_space_rtc_init (0x4234c-0x423cb), which is no longer called.
CLOCK_LIMIT = 0x423CC - 0x4234C


def patched(original, clock):
    if hashlib.sha256(original).hexdigest() != PLAYER_SHA256:
        raise ValueError("Input is not the original RX3 1.19 rbp; patch addresses would be wrong")
    if not clock or len(clock) > CLOCK_LIMIT or len(clock) % 4:
        raise ValueError("pi-clock.bin has an unexpected size; rebuild it with build.sh")
    p = bytearray(original)

    def patch(a, v):
        p[a - 0x8000 : a - 0x8000 + len(v)] = v

    def words(a, *v):
        patch(a, struct.pack("<" + "I" * len(v), *v))

    def branch(a, b, link=False):
        return (0xEB000000 if link else 0xEA000000) | (((b - a - 8) // 4) & 0xFFFFFF)

    words(0x10284, 0xE320F000)
    patch(0x4234C, clock)
    words(0x42318, branch(0x42318, 0x4234C))
    words(0x42330, 0xE92D4010, branch(0x42334, 0x4234C, True), 0xE300314D, 0xE0810390, 0xE8BD8010)
    patch(0x443454, b"debug\0")
    words(0x1A3AB8, 0xE3003C03)
    words(0x1A3AC0, 0xE3403040)
    # Original GPIO interrupts do not exist on the Pi; retain emulated initial states.
    words(0x28AC8, 0xE12FFF1E)
    # Select the existing audio profile; PCM devices are redirected by fbshim.
    words(0x3C6654, 0xE3A00001)
    return bytes(p)


if __name__ == "__main__":
    b = Path(__file__).resolve().parent.parent
    args = [Path(a) for a in sys.argv[1:]]
    if len(args) not in (0, 3):
        sys.exit(__doc__)
    source, clock, output = args or (b / "pi-runtime/rbp", b / "pi-clock.bin", b / "rbp-pi")
    try:
        result = patched(source.read_bytes(), clock.read_bytes())
    except (OSError, ValueError) as error:
        sys.exit(f"patch-player.py: {error}")
    output.write_bytes(result)
    output.chmod(0o755)
    print(f"Created {output}")
