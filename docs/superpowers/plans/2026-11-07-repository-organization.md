# Repository Organization Implementation Plan

> **For agentic workers:** Execute this plan inline; use the requesting-code-review skill before publishing the PR.

**Goal:** Make the project easier to navigate while preserving the supported setup, build and launch commands.

**Architecture:** Keep user entry points and the Python CLI package in place. Group native sources, tests, documentation and generated-asset tools by purpose, and update their callers together.

**Tech Stack:** Python 3.9+, POSIX shell, C, ARM assembly, Markdown.

## Global Constraints

- Keep `./rx3`, `sh build.sh native`, `sh build.sh shim RUNTIME` and compatibility launch/recovery entry points working.
- Preserve source history and third-party notices; do not assign a new license.
- Keep the GitHub repository private and open a PR without merging it.
- Do not download firmware or run hardware tests on this Mac.

### Task 1: Group implementation files and tests

**Files:** Move root C/header/assembly/linker-map files into `src/native/`; C tests into `tests/native/`; replay scripts into `tests/replay/`; live-device scripts into `tests/hardware/`; audio integration shell scripts into `tests/integration/`.

**Interfaces:** Existing build outputs and CLI commands remain unchanged. Native compiler commands receive `-I src/native`; Python replay scripts locate the root through `Path(__file__).resolve().parents[2]`.

- [x] Move tracked files by category, leaving Python runtime entry points in place.
- [x] Update source paths in `build.sh`, `build-audio-candidate.sh`, integration shell scripts, replay scripts and `rx3tool/cli.py`. Resolve integration script working directories to the repository root.
- [x] Verify Python syntax, shell syntax, FLX4 tests, six portable replay suites and portable native tests. Record Linux-only checks that cannot run on macOS.

### Task 2: Organize documentation and development tools

**Files:** Move root research Markdown into `docs/`, screenshots into `docs/images/`, and `generate-*.py` into `tools/glyphs/`. Add `CONTRIBUTING.md` and `tests/README.md`; update `README.md` and moved documentation links.

**Interfaces:** Glyph generators write to `src/native/` using paths relative to their own files, regardless of the caller's working directory. Root `THIRD-PARTY-NOTICES.md` remains discoverable.

- [x] Move files and update generator output locations and documentation paths.
- [x] Replace the obsolete upstream review-branch clone instructions with this private repository's main branch; document the folder map and contributor commands.
- [x] Check local Markdown links, inspect the diff, and request independent review.

### Task 3: Publish a private reviewable PR

- [x] Push the preserved combined source history as `main` to the empty private repository, then push the organization branch.
- [x] Open a PR describing the before/after organization, preserved commands, validation results and remaining platform limits. Do not merge.

## Validation record

- Python syntax (41 files), shell syntax, local Markdown links and CLI help passed.
- Three FLX4 unit tests, six replay suites (also invoked from outside the checkout) and eight portable native tests passed.
- All 60 native source and C test files are byte-for-byte moves; root entries dropped from 114 to 28.
- Full selftest still fails on this Mac: missing `cryptography`, two existing Linux path assumptions, missing Linux touch headers and libdrm build dependencies. An additional audio-handles compile needs Linux `EBADFD`. No physical hardware or ARM32 runtime validation was run.
- Independent review found missing include flags in moved documentation examples; these were corrected to `-I src/native`.

Private review PR: https://github.com/swrzalek/pi-rx3/pull/1 (opened, not merged).
