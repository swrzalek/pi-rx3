# Guided Configuration Implementation Plan

**Goal:** Configure controller, audio, music USB, display and touch interactively using `./rx3 start --config`, then start normally.

**Architecture:** A dedicated wizard uses existing detection and validation APIs, preserves unrelated file settings, previews changes, and saves atomically. CLI keeps global `--config FILE` separate from the start flag.

**Tech Stack:** Python standard library, unittest.

## Constraints

Python 3.9+, no new dependencies. FLX4 remains experimental. Dry runs must not save or download. Do not persist environment or command-line overrides.

### Task 1: Wizard and CLI

- [ ] Add `rx3tool/wizard.py`: numbered choices with current defaults; controller profiles; ALSA, USB, DRM and touch selection; preview, confirmation and atomic persistence.
- [ ] Add start `--config` and `config wizard`; preserve global file selection. Run mapping validation before starting.
- [ ] Add offline tests for FLX4 selection, cancellation, override preservation, noninteractive input, dry-run and CLI routing.
- [ ] Run `python3 -m unittest discover -s tests` and review diff.
- [ ] Document commands and limits in README and setup guide.
