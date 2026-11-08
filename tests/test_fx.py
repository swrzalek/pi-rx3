"""FLX4 Beat FX mapping and feedback without hardware."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests.test_flx4_mapping import bridge, ROOT


class FXTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.now = 0
        self.b = bridge.Bridge(str(ROOT / 'mappings/Pioneer-DDJ-FLX4.rx3.xml'),
                               lambda *e: self.events.append(e), lambda: self.now)

    def test_buttons_ignore_duplicate_presses_and_release_once(self):
        for status,note,key in [(0x94,0x47,0x448d),(0x95,0x47,0x448d),
                                (0x94,0x4a,0x4490),(0x94,0x4b,0x4491)]:
            self.events.clear()
            for value in (127,127,0,0): self.b.message(status,note,value)
            self.assertEqual(self.events, [(key,0,0,0,0.,0),(key,2,0,0,0.,0)])

    def test_selection_and_depth(self):
        for note,direction in [(0x63,1),(0x64,-1)]:
            self.events.clear()
            for value in (127,127,0): self.b.message(0x94,note,value)
            self.assertEqual(self.events,[(0x448b,5,0,direction,0.,0x4658)])
        self.events.clear()
        for v in (0,127): self.b.message(0xb4,2,v)
        self.assertEqual([e[4] for e in self.events],[0.,1.])
        self.assertTrue(all(e[:3]==(0x448f,4,0) for e in self.events))

    def test_channel_switch_coalesces_both_messages(self):
        for left,right,target in [(127,0,0),(127,127,5),(0,127,1),(0,0,5)]:
            self.b.message(0x94,0x10,left)
            self.b.message(0x95,0x11,right)
            self.now+=.03;self.b.tick()
            self.assertEqual(self.events[-1],(0x448c,5,0,target,0.,0))

    def test_blink_native_state_missing_invalid_and_stale(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state'
            self.assertEqual(bridge.fx_led_value(path),0)
            path.write_bytes(b'\x01\x00\x00\x00')
            with patch.object(bridge.time,'monotonic',return_value=0):
                self.assertEqual(bridge.fx_led_value(path),127)
                self.assertEqual(bridge.fx_led_value(path,now=path.stat().st_mtime+3),0)
            with patch.object(bridge.time,'monotonic',return_value=.25):
                self.assertEqual(bridge.fx_led_value(path),0)
            for data in (b'',b'\x02\x00\x00\x00',b'\x00\x00\x00\x00'):
                path.write_bytes(data)
                self.assertEqual(bridge.fx_led_value(path),0)

    def test_disconnect_cancels_pending_routing_and_releases_toggle(self):
        self.b.message(0x94,0x47,127)
        self.b.message(0x94,0x10,127)
        self.b.release()
        self.now=1;self.b.tick()
        self.assertEqual(self.events,[(0x448d,0,0,0,0.,0),(0x448d,2,0,0,0.,0)])

    def test_output_failure_retries_without_raising_into_input(self):
        from unittest.mock import Mock
        lib=Mock()
        lib.snd_rawmidi_open.return_value=0
        lib.snd_rawmidi_write.return_value=-19
        running=iter([True,False])
        bridge.cue_feedback(lib,lambda:next(running),lambda:['hw:2,0,0'], '/missing/rx3-cue-state')
        lib.snd_rawmidi_close.assert_called_once()
