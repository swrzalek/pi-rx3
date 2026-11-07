#!/bin/sh
# Compatibility name for ./rx3 start (settings come from rx3.conf; see README).
here=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
if [ ! -f "$here/rx3tool/launch.py" ]; then
 echo "start-rx3.sh now needs the rest of the rx3-pi checkout. Run ./rx3 start from the checkout." >&2
 exit 2
fi
exec python3 "$here/rx3" start "$@"
