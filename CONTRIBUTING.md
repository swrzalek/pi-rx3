# Contributing

See [architecture](docs/architecture.md) to locate implementation files and [setup](docs/setup.md) for Linux build prerequisites. Python 3.9+ is required. Run from the repository root:

```sh
./rx3 --help
./rx3 selftest
sh build.sh native
# With an assembled ARM32 runtime:
sh build.sh shim /absolute/path/to/runtime
git diff --check
```

Build outputs stay in `build/` or `RX3_BUILD`. [The test guide](tests/README.md) lists individual checks and hardware requirements. Full selftest targets Linux; portable subsets can run on macOS.

Glyph generators in `tools/glyphs/` require ImageMagick (`magick`) and Liberation Sans. For example, `python3 tools/glyphs/generate-native-labels.py` writes its header to `src/native/`, independent of the caller's working directory. Review generated changes before committing.

PRs should describe affected behavior, checks run and hardware still untested. Keep file moves separate from behavior changes where practical. Do not commit local configuration, firmware, keys, music, runtime state or build outputs. Preserve [authorship and notices](THIRD-PARTY-NOTICES.md); no project-wide reuse license has been established.

## Formatting

Install the pinned development tools in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tools/format.py
python tools/format.py --check
```

Ruff formats Python (including `rx3`), and clang-format formats C sources and
headers. The wrapper includes tracked and new, non-ignored files. Generated
`*-glyphs.h` headers are excluded; change their generators instead. Local
runtime and build files are excluded. CI runs the same check on pushes and PRs.
Formatting is development tooling only and adds no runtime dependencies.
