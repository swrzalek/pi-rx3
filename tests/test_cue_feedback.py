"""FLX4 feedback protocol regression."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from rx3tool import REPO

spec = importlib.util.spec_from_file_location(
    "cue_bridge", REPO / "scripts/controllers/midi-rx3.py"
)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class CueTests(unittest.TestCase):
    def test_snapshot_packets_and_shutdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cue"
            path.write_bytes(b"\x01\x00\x00\x00")
            lib = Mock()
            lib.snd_rawmidi_open.return_value = 0
            lib.snd_rawmidi_write.return_value = 3
            running = iter([True, True, False])

            def sleep(_):
                path.write_bytes(b"\x02\x00\x00\x00")

            bridge.cue_feedback(lib, lambda: next(running), lambda: ["hw:1,0,0"], path, sleep)
            all_packets = [call.args[1] for call in lib.snd_rawmidi_write.call_args_list]
            packets = [packet for packet in all_packets if packet[1] == 0x54]
            self.assertEqual(
                [p for p in all_packets if p[1] == 0x47], [b"\x94\x47\x00", b"\x94\x47\x00"]
            )
            self.assertEqual(
                packets,
                [
                    b"\x90\x54\x7f",
                    b"\x91\x54\x00",
                    b"\x90\x54\x00",
                    b"\x91\x54\x7f",
                    b"\x90\x54\x00",
                    b"\x91\x54\x00",
                ],
            )
            lib.snd_rawmidi_close.assert_called_once()
