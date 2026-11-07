# Audio recovery

The native RX3 playback error branch expects vendor DMA hardware. The shim intercepts managed ALSA output errors before that branch; do not expose `/dev/mem` to make vendor recovery run.

## Implementation

All sources are in `src/native/`:

- `audio-proxy`: interposes handle-bearing ALSA calls and serializes setup/write/close; unrelated streams pass through.
- `audio-recovery`, `audio-alsa`: coordinate master/cue replacement with bounded retry/backoff, rebuilding hardware constraints and restoring software parameters.
- `audio-handles`: keep caller-visible tokens stable across replacement and reject retired/duplicate handles.
- `audio-write`, `audio-pacer`: bound write retries and pace unavailable output. Paired master/cue blocks share a monotonic deadline; unavailable writes return paced EPIPE rather than fictitious accepted frames.

`build.sh` includes these through `scripts/build/build-audio-candidate.sh`. Link against the assembled ARM32 libraries: glibc 2.13 needs the 32-bit time ABI, and near-setting wrappers resolve the ALSA_0.9.0rc4 symbols explicitly. Preserve `fbshim-audio.map` symbol versions.

## Evidence and limits

Inherited development records report null-PCM and embedded-runtime checks for repeated pair replacement, persistent absence, parameter preservation, rollback, token lifetime, close ordering and paired pacing. Reopening real FLX6 plug/route/dmix outputs required rebuilding constraints rather than reapplying an opaque hardware-parameter snapshot.

A deployed development player survived sysfs removal/rebinding of all FLX6 `snd-usb-audio` interfaces: pair state changed OFFLINE → LIVE with replacement handles while the PID stayed the same. Both decks produced changing output buffers afterward; MIDI reconnected too. Releasing only the primary interface had failed because remaining interfaces retained a shutdown card instance.

This evidence does **not** prove uninterrupted audible playback, physical cable-unplug behavior, real hardware card renumbering, successful hardware-link replay or fresh-boot reliability. It was not repeated during repository cleanup.

## Checks

Use the commands and prerequisites in [tests](../tests/README.md). `tests/integration/` contains isolated null-PCM and ARM32 runtime harnesses. Never preload a test constructor harness into the player.

`tests/hardware/test-audio-live-state.py` is read-only but requires a local build matching the deployed shim. `test-audio-live-reconnect.py` disrupts real hardware and requires root, a matching build, paused decks and the FLX6 at card 2. It is excluded from selftest. The runtime integration script's `--flx6` mode uses real outputs; stop the player and other audio owners first.
