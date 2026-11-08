# pi-rx3

Experimental RX3 1.19 player compatibility on Raspberry Pi 5, with display, touch, MIDI and audio helpers. This runs the embedded player; it is not desktop rekordbox or firmware to flash onto the Pi.

## Start here

Use **`./rx3`** for setup and operation. Follow [setup and troubleshooting](docs/setup.md), then:

```sh
./rx3 config init
./rx3 doctor
./rx3 setup
./rx3 start
# When finished:
./rx3 stop
```

Requires a Pi 5, 64-bit Raspberry Pi OS/Debian with ARM32 support and Python 3.9+, a supported display, and a controller/audio interface. The tested configuration uses FLX6; FLX4 is experimental. Supported display modes are 1200×1920 portrait and 1024×600/1024×768 landscape.

Fresh installation on a second physical Pi, full FLX4 routing and landscape touch acceptance remain unverified. See [validation and limitations](docs/validation.md).

## Project map

| Folder | Purpose |
| --- | --- |
| `rx3tool/` | Setup/launch CLI, firmware recovery and player patching |
| `src/native/` | Native display, touch, audio and player compatibility code |
| `scripts/` | Build, controller, firmware, compatibility and legacy utilities |
| `config/`, `mappings/` | Configuration templates and controller profiles |
| `tests/`, `tools/glyphs/` | Tests and UI glyph generators |
| `docs/` | [Setup](docs/setup.md), [architecture](docs/architecture.md), [controllers](docs/controllers.md), [audio recovery](docs/audio-recovery.md), [validation](docs/validation.md) |

[Contributing](CONTRIBUTING.md) covers development; [tests](tests/README.md) distinguishes offline checks from hardware tests. Local outputs go to ignored `build/` and `work/` directories.

## Origin and permissions

This private repository combines [upstream PR #1](https://github.com/xsploit/rx3-pi/pull/1) and [PR #4](https://github.com/xsploit/rx3-pi/pull/4), preserving their history. No project-wide license has been identified; broader reuse and redistribution permission remains unresolved. Keep the [third-party notices](THIRD-PARTY-NOTICES.md). Firmware, keys, proprietary libraries and music are recovered or supplied locally, not distributed here.

For guided device setup, connect your controller, screen and music USB, then run:

```sh
./rx3 start --config
```

Choose FLX4 (experimental) or FLX6, the controller audio card, a FAT32 music
USB, display and touchscreen. Enter keeps the current setting. Review and
confirm to save `rx3.conf` and continue startup; later runs only need
`./rx3 start`. FLX4 uses the included mapping; a missing FLX6 mapping is
downloaded and verified automatically. Normal prerequisite checks still apply.
Use `./rx3 config wizard` to save settings without starting. To use another
settings file: `./rx3 --config /path/to/settings.conf start --config`.
`./rx3 start --config --dry-run` previews selections without saving them.
