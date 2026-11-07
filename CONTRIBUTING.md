# Working on pi-rx3

Start with the [setup guide](README.md) for supported hardware and dependencies. The project targets Raspberry Pi OS / Debian with Python 3.9+; several tests and all device helpers require Linux.

## Find the right files

- `rx3tool/` implements recovery, assembly, installation, validation and process management. `rx3` is the user entry point.
- `src/native/` contains the player shim, audio adapters, display presenter, touch bridge and native UI. Keep its generated glyph headers beside the consumers.
- `tests/` groups unit tests, native tests, replay checks, audio integration tests and live hardware checks. See the [test guide](tests/README.md).
- `mappings/` holds controller XML profiles and supported-control notes.
- `docs/` holds validation records and historical research. Screenshots live in `docs/images/`.
- `tools/glyphs/` regenerates glyph headers. The generators require ImageMagick (`magick`) and the Liberation Sans font; outputs go directly to `src/native/`.

The root build scripts and Python runtime utilities remain stable entry points. `prepare-runtime.py` and `prepare-library-view.sh` are historical experiments, not the supported installer.

## Build and check a change

From the repository root on Linux, with the README prerequisites installed:

```sh
./rx3 --help
./rx3 selftest
git diff --check
```

Selftest is offline: it does not recover firmware, mount a runtime or start the player. It builds native helpers, so it still requires the Linux headers, libdrm and FreeType development packages. Python recovery tests require `cryptography`.

Build outputs continue to go to `build/` (or `RX3_BUILD`):

```sh
sh build.sh native
sh build.sh shim /absolute/path/to/assembled/runtime
```

To regenerate an individual glyph header:

```sh
python3 tools/glyphs/generate-native-labels.py
```

The generator resolves its output relative to its own location, so running it from another working directory is supported. Review generated changes before committing.

## Review expectations

Describe the behavior affected, checks run and hardware still untested. Keep code moves separate from behavior changes where practical. Do not commit local configuration, firmware, recovered keys, music, runtime state or build products; those paths are ignored.

Preserve authorship and [third-party notices](THIRD-PARTY-NOTICES.md). This checkout has no identified project-wide license; keeping it private does not grant additional rights. Broader reuse or redistribution requires resolving permission with the relevant rights holders.
