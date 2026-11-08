"""Native user FX state must be off even when internal engine enable persists."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from rx3tool import REPO


@unittest.skipUnless(shutil.which("cc"), "host C compiler required")
class NativeFXStateTests(unittest.TestCase):
    def test_user_toggle_and_missing_objects(self):
        source = r"""
#include <assert.h>
#include <string.h>
#include "fx-state.h"
int main(void) {
    uintptr_t root[64] = {0}, mixer[64] = {0}, master[64] = {0};
    assert(rx3_fx_enabled(0) == 0);
    assert(rx3_fx_enabled(root) == 0);
    *(void **)((char *)root + 0x50) = mixer;
    assert(rx3_fx_enabled(root) == 0);
    *(void **)((char *)mixer + 0xa8) = master;
    unsigned char *enabled = (unsigned char *)master + 0x44;
    *enabled = 1; assert(rx3_fx_enabled(root) == 1);
    *enabled = 0; assert(rx3_fx_enabled(root) == 0);
    *enabled = 1; assert(rx3_fx_enabled(root) == 1);
    *enabled = 2; assert(rx3_fx_enabled(root) == 0);
}
"""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "test.c").write_text(source)
            subprocess.run(
                [
                    "cc",
                    "-I",
                    str(REPO / "src/native"),
                    str(path / "test.c"),
                    "-o",
                    str(path / "test"),
                ],
                check=True,
                capture_output=True,
            )
            subprocess.run([str(path / "test")], check=True)
