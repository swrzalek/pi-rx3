# Tests

Run from the repository root. See [setup prerequisites](../docs/setup.md) for Linux packages.

| Folder | Checks | Requirements |
| --- | --- | --- |
| `test_*.py` | Setup, recovery and FLX4 unit tests | Python 3.9+, `cryptography`; setup tests assume Linux paths |
| `native/` | C frame, mixer, input and audio tests | Compiler; some need Linux headers, libdrm, FreeType or ALSA |
| `replay/` | Synthetic MIDI and touch input | Python; touch replay compiles the Linux bridge |
| `integration/` | ALSA null-PCM and ARM32 runtime harnesses | Linux/ALSA; runtime harnesses require assembled runtime and sudo |
| `hardware/` | Live audio state/reconnect and uinput | Configured Pi/devices; some require root |

```sh
./rx3 selftest
# Individual checks:
python3 -m unittest tests.test_flx4_mapping
python3 tests/replay/test-navigation.py
sh build.sh native
./build/test-frame-scale
# Isolated host ALSA check:
sh tests/integration/test-audio-proxy.sh
```

Selftest runs Python tests, seven replay suites and nine native tests; no firmware or physical controller is needed. Six MIDI/navigation replays and the FLX4 tests run on macOS; the complete suite needs Linux.

`test-audio-alsa-runtime.sh` and `test-audio-proxy-runtime.sh` under `integration/` accept an absolute runtime path. They compile temporary libraries into that runtime and use chroot/sudo; the proxy script defaults to null PCMs, while `--flx6` uses real outputs. Read scripts before running hardware checks: reconnect tests disrupt devices and are excluded from selftest. Never preload a test constructor harness into the player. Record physical evidence separately in [validation](../docs/validation.md).
