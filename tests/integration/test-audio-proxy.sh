#!/bin/sh
# Host null-PCM integration test; no hardware access.
set -eu
cd "$(dirname "$0")/../.."
test_dir=$(mktemp -d)
trap 'rm -rf "$test_dir"' EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
"${CC:-cc}" -I src/native -std=gnu11 -O2 -Wall -Wextra -Werror -shared -fPIC \
 -DRX3_AUDIO_PROXY_TEST -Wl,--version-script=src/native/audio-proxy.map \
 -o "$test_dir/proxy.so" src/native/audio-proxy.c src/native/audio-alsa.c src/native/audio-recovery.c \
 src/native/audio-handles.c src/native/audio-write.c src/native/audio-pacer.c -lasound -ldl -pthread
"${CC:-cc}" -I src/native -std=gnu11 -O2 -Wall -Wextra -Werror \
 -o "$test_dir/test" tests/native/test-audio-proxy.c -lasound -ldl
cat > "$test_dir/alsa.conf" <<'CONFIG'
pcm.rx3out { type null }
pcm.rx3cue { type null }
pcm.null { type null }
CONFIG
ALSA_CONFIG_PATH="$test_dir/alsa.conf" LD_PRELOAD="$test_dir/proxy.so" "$test_dir/test"
