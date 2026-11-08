# Architecture

The root `rx3` command dispatches into `rx3tool/cli.py`. Native helpers and the embedded ARM32 player run separately; the player and shim must be built as a matched pair for firmware 1.19.

| Component | Location and responsibility |
| --- | --- |
| Recovery | `rx3tool/recover.py`, `firmware_image.py`, `cramfs.py`: pinned downloads, decryption, extraction |
| Runtime | `rx3tool/assemble.py`, `safefs.py`, `elfdeps.py`: confined assembly, manifests and dependency checks |
| Installation | `rx3tool/install.py`, `patch_player.py`, `patch_tempo25.py`: guarded player patches and matched shim installation |
| Configuration/launch | `rx3tool/config.py`, `doctor.py`, `launch.py`, `system.py`: settings, prerequisites, mounts, scoped processes |
| Graphics/touch | `src/native/fb-present.c`, `drm-present.h`, `frame-*.h/.c`, `touch-bridge.c`: complete-frame presentation, scaling and evdev translation |
| Player/UI | `src/native/fbshim.c`, `control-shim.c`, `native-*.c/.h`: compatibility hooks and native control surfaces |
| Audio | `src/native/audio-*.c/.h`: ALSA interposition, paired recovery, stable handles, bounded writes and pacing |
| MIDI | `scripts/controllers/midi-rx3.py`: XML input translation, controller discovery and reconnect |
| Templates | `config/asound.conf`, `config/rx3.conf.example`; generated user settings remain at root `rx3.conf` |

The runtime owns emulated devices, patched player/libraries and a local writable library view. Original music is mounted read-only. Shared complete-frame buffers decouple presentation from native redraw; the control FIFO carries translated input. [Audio recovery](audio-recovery.md) describes the ALSA boundary.

## Utilities

- `build.sh` is the supported native/shim build entry point; its ARM32 helper lives in `scripts/build/`.
- `scripts/controllers/pi-control.py` sends native control events; `touch-replay.py` replays touch through the Linux bridge. Both require `RX3_RUNTIME`.
- `scripts/firmware/extract_cramfs.py` is an extraction helper, not the full runtime assembler.
- `scripts/compat/` contains the old recover/start/stop names, forwarding to `./rx3` from their new locations. Update any external paths that called root-level copies.
- `scripts/legacy/` contains the old machine-specific runtime/library preparation experiments. They retain historical assumptions and are not used by the current installer.
- `tools/glyphs/` generates checked-in headers. Tests live under `tests/`; [key codes](reference/keycodes.txt) and screenshots in `docs/images/` are reference material.

Long chronological research diaries were removed from the current docs during cleanup; the original files remain available in Git history. Current operating instructions live only in [setup](setup.md), and evidence/unfinished work in [validation](validation.md).

## MIDI dispatch

The bridge compiles FLX4/FLX6 XML profiles once at startup. `Bridge.feed`
parses MIDI bytes; `Bridge.message` normalizes NoteOff and dispatches to a
bound handler by mode. `MidiHandlers` keeps buttons, jogs, pads, analog input,
14-bit values and FX behavior separate. Stateful ownership and disconnect
cleanup remain shared by the bridge. Profile classification is outside the
message path; no per-message file access, sleeps or threads were added.

To compare a saved earlier bridge with the current implementation, run
`python3 tools/benchmark-midi.py /path/to/baseline-midi.py`. It first compares
emitted commands for a deterministic mixed replay, then reports median Python
dispatch time for jog, depth and FX button messages. This does not measure USB,
queue delivery, Pi scheduling or audible latency; those require hardware.
