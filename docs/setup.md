# Setup and operation

Run commands from the checkout as your normal account, not `sudo ./rx3`. The launcher requests sudo for mounts and chroot.

## Requirements

- Raspberry Pi 5 (tested with 4 GB), 64-bit Raspberry Pi OS/Debian, Python 3.9+, ARM32 execution and a 4 KiB-page kernel.
- Display: 1200×1920 portrait or 1024×600/1024×768 landscape. DRM supports a 16-bit console; fbdev fallback requires 32 bits. The 1024×600 image fills the panel with a changed aspect ratio.
- FLX6 audio/MIDI: four channels at 44.1 kHz, master on 1/2 and headphones on 3/4. [FLX4 configuration and limitations](controllers.md) are experimental.
- A Linux filesystem such as ext4 for the runtime, with at least 1 GB free. A FAT32 rekordbox-export USB can supply music; exFAT remains untested.
- Firmware **1.19 only**. Fixed-address patches reject other binaries; this is a supported-version pin, not a claim about the latest release.

## Install

```sh
sudo apt update
sudo apt install git python3 python3-cryptography build-essential pkg-config \
  libdrm-dev libfreetype-dev gcc-arm-linux-gnueabi binutils-arm-linux-gnueabi \
  libc6-dev-armel-cross linux-libc-dev unzip libarchive-tools \
  alsa-utils libasound2 fonts-dejavu-core sudo util-linux mount

git clone https://github.com/swrzalek/pi-rx3.git
cd pi-rx3
./rx3 config init
./rx3 doctor --stage recover --stage build
./rx3 setup
```

Cloning requires access to the private repository. Fix doctor failures before setup. Setup downloads about 322 MB of checksum-pinned official ZIPs, recovers the key, assembles a runtime, builds and installs a matched player/shim, then validates it. It fetches a pinned public FLX6 XML if your configured mapping is missing. Expected completion: `Setup finished`.

| Output | Contents |
| --- | --- |
| `work/downloads/` | Verified official ZIPs, retained for reuse |
| `work/firmware/` | Private `aes256.key` and verified `images/` |
| `work/runtime/` | Assembled runtime, patched `root/pdj/rbp-pi` and `lib/fbshim.so` |
| `build/`, `work/state/logs/` | Compiled helpers and startup logs |

Recovery resumes interrupted downloads and reuses verified inputs. Existing official ZIPs can be supplied with `./rx3 setup --from /path/to/zips`; names do not matter, hashes do. A key or joined tarball alone is not a runnable installation. For offline setup, retain the three official ZIPs and fetch the mapping first with `./rx3 mapping`, then run `./rx3 setup --offline --from /path/to/zips`.

Official inputs: [source packages](https://www.pioneerdj.com/en/support/open-source-code-distribution/gnu-open-source-license/) and [firmware](https://support.alphatheta.com/en-US/articles/4562999179673). Pinned URLs/hashes live in [recover.py](../rx3tool/recover.py) and [mapping.py](../rx3tool/mapping.py). Missing upstream inputs cause a failure rather than a version substitution.

## Configure and run

```sh
lsblk -o NAME,FSTYPE,UUID,LABEL,MOUNTPOINTS
```

Set `[usb] uuid` in the generated root `rx3.conf` to the music partition UUID; leave it empty to boot without music. Use a rekordbox export with `PIONEER/rekordbox/export.pdb`; loose-track copying is not tested. Close Mixxx/BiteDJ and log out of the desktop so RX3 can own the controller and display.

```sh
./rx3 doctor
./rx3 start --dry-run
./rx3 start
./rx3 status
./rx3 stop
```

The original USB is mounted read-only. Database/analysis are copied to a writable local view at `work/runtime/media/usb2/sdb1`; music stays on USB under `Contents`, `Music` or `PIONEER/Artwork`. Local edits are not written back to USB. A changed USB UUID needs a separate runtime. Re-exporting the same USB does not refresh an existing local database automatically: back up the old runtime and create a new one.

## Configuration and maintenance

The [template](../config/rx3.conf.example) documents settings. Relative paths resolve against the **generated config file's folder**, not the template folder. Precedence is defaults → config file → `RX3_SECTION_KEY` environment → `--set section.key=value`. Work, runtime, state, build and mapping paths are separate settings.

```sh
./rx3 config show
./rx3 --set usb.uuid=1234-ABCD start
./rx3 --config /path/to/another.conf doctor
./rx3 setup --dry-run
```

Individual stages are `mapping`, `recover`, `assemble`, `build`, `install` and `validate`; each supports `--help`. Build/install require the player stopped. After changing the audio card, repeat assemble → build → install. Install retains changed player/shim files as `.previous`; manifests detect mismatched or interrupted installation. `assemble --repair` rewrites firmware files, including settings, so back up customizations first.

Use a **new empty runtime** rather than an old hand-assembled rootfs. Stop the old installation with its own launcher and keep its settings/library as backup. [Legacy utilities](architecture.md#utilities) are not the supported setup path.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Missing `xf86drm.h`, compiler or ARM headers | Install prerequisites above; run `./rx3 doctor --stage build`. |
| Recovery killed or incomplete | Rerun the same command; inspect `journalctl -k -b` for OOM evidence. |
| ARM32 execution fails / 16 KiB pages | Follow doctor's kernel guidance (`kernel=kernel8.img` in `/boot/firmware/config.txt`), reboot and recheck. |
| `vm.mmap_min_addr` blocks startup | Follow doctor's guidance for 32768 or lower; settings are not changed automatically. |
| Device permission denied | Follow doctor's group advice (`audio`, `video`, `render`, `input`); log out/in afterward. |
| Missing display or wrong geometry | Run doctor; configure DRM/touch paths if auto-detection is ambiguous. Check supported modes above. |
| Player/helper exits | Read `player.log`, `display.log`, `touch.log`, `midi.log` under `work/state/logs/`; run stop before retrying. |
| USB already mounted without UTF-8 | Unmount it in the desktop without unplugging, then retry. |
| Another installation owns devices | Stop it with its own launcher; this launcher scopes process cleanup to its configured runtime. |
