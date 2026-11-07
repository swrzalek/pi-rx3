# Validation and remaining work

Separate inherited development evidence from checks performed on this reorganized checkout. Builds, screenshots and synthetic input do not establish physical acceptance.

## Inherited evidence

| Scope | Recorded result | Limit |
| --- | --- | --- |
| Setup workflow, Linux x86_64 (2026-09-11) | Fresh checkout with spaces; pinned recovery, repeated assembly, native/ARM32 builds, matched installation, manifests and ELF dependencies; offline/dry-run paths | No physical Pi installation; native host helpers still need rebuilding on the Pi |
| Development Pi | Browsing/loading, playback, stacked waveforms, native transport/mixer/touch and controller input | One existing installation; touch replay is not physical finger testing |
| Complete-frame exchange | Racing-writer checks and final stable-frame verification passed | Does not establish native compositor quality; waveform flicker/cadence remains unresolved |
| Audio device loss | Same-player recovery after sysfs FLX6 interface removal/rebinding, with subsequent output buffers | See [audio recovery limits](audio-recovery.md); no uninterrupted-audio or physical cable claim |
| Landscape / FLX4 work | Prior user-confirmed 1024×600 playback and offline profile tests | Physical FLX4 retest, landscape touch/audio acceptance and 1024×768 testing remain open |

Original chronological diaries and exact historical measurements remain in Git history. They are not current setup instructions.

## Repository cleanup checks

- Python and shell syntax, local documentation links and CLI help.
- Three FLX4 unit tests; six portable MIDI/navigation replay suites, also invoked outside the checkout.
- Eight portable native tests: scaling, mixer layout/state, tempo step/input, pad bank/intent and audio recovery.
- Native implementation/C test contents preserved during moves.

Full selftest was attempted on macOS. Missing `cryptography`, existing Linux filesystem assumptions, Linux input headers and libdrm dependencies prevent a complete pass. An extra audio-handles compile also needs Linux `EBADFD`. No new firmware recovery, Linux/ARM32 build or physical hardware acceptance is claimed for cleanup.

## Physical acceptance still needed

On a separately prepared supported Pi, follow [setup](setup.md) from a fresh checkout, then check:

1. Doctor, cold boot, launch and restart without machine-specific edits.
2. Display geometry and touch alignment across the screen, both landscape modes, browse/back/view and both deck loads.
3. Both decks' play/cue, jog/tempo, mixer controls, master/headphone routing and FLX4 behavior.
4. Correct USB library, read-only original media, locally preserved edits and clean stop/restart.
5. Real MIDI/audio disconnect/reconnect, physical touch/pad combinations, waveform cadence and remaining FX/LED controls.

ExFAT, broader audio interfaces, general touch/MIDI pad ownership and universal controller compatibility remain unverified. Do not mark these complete from offline tests alone.
