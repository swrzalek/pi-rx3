# Tests

Run commands from the repository root unless noted otherwise.

| Location | Purpose | Requirements |
| --- | --- | --- |
| `test_*.py` | Python unit tests for setup, recovery and the FLX4 profile | Python 3.9+, `cryptography`; setup tests assume Linux filesystem paths |
| `native/` | C regressions for frame exchange, scaling, input, mixer and audio | C compiler; some tests need Linux, libdrm, FreeType or ALSA |
| `replay/` | Synthetic MIDI and touch input checks | Python; touch replay also compiles the Linux touch bridge |
| `integration/` | ALSA null-PCM and runtime integration scripts | Linux and ALSA; runtime scripts need an assembled ARM32 runtime and sudo |
| `hardware/` | Live audio state/reconnect and Linux uinput checks | Configured Pi/device environment; read each script before running |

## Offline checks

```sh
./rx3 selftest
```

This runs Python unit tests, seven replay scripts and nine native tests. It requires the build dependencies from the README but no firmware, running player or physical controller. It does not run the integration or hardware scripts.

For individual checks:

```sh
python3 -m unittest tests.test_flx4_mapping
python3 tests/replay/test-navigation.py
sh build.sh native
./build/test-frame-scale
```

The six MIDI/navigation replay scripts and FLX4 tests can run on macOS. The complete suite targets Linux: macOS lacks `linux/input.h`, and existing setup tests assume Linux `/etc` and temporary-directory paths.

## Integration and hardware checks

The host null-PCM test uses isolated ALSA configuration and does not access hardware:

```sh
sh tests/integration/test-audio-proxy.sh
```

The runtime integration scripts accept the assembled runtime as their first argument. They compile test libraries into that runtime and invoke chroot through sudo. Read the scripts before running them:

```sh
sh tests/integration/test-audio-alsa-runtime.sh /absolute/path/to/runtime
sh tests/integration/test-audio-proxy-runtime.sh /absolute/path/to/runtime
```

`test-audio-proxy-runtime.sh` uses null PCMs by default; its `--flx6` option uses real outputs. Hardware scripts can inspect or reconnect devices, and the uinput check needs root. They are deliberately excluded from selftest. Record physical results separately from offline checks in [setup validation](../docs/SETUP-VALIDATION.md).
