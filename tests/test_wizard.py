"""Offline regression tests for interactive configuration."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rx3tool.config import load
from rx3tool.wizard import configure, update_setting, usb_choices
from rx3tool.ui import Failure
from rx3tool.cli import main


class WizardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "settings.conf"
        self.path.write_text("# keep this\n[paths]\nwork = custom\n[audio]\ncard = DDJFLX6\n")
        self.config = load(self.path, env={})
        for name, value in [
            ("alsa_cards", {}),
            ("usb_choices", [("B9C8-1E1B", "Music")]),
            ("detect_drm_cards", []),
            ("detect_touchscreens", []),
        ]:
            patcher = patch("rx3tool.wizard." + name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch("rx3tool.wizard.sys.stdin.isatty", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_flx4_and_usb_saved_preserving_unrelated_settings(self):
        with patch("builtins.input", side_effect=["1", "", "2", "", "", "y"]):
            result = configure(self.config)
        self.assertEqual(result.get("controller", "midi_name"), "DDJ-FLX4")
        self.assertEqual(result.get("audio", "card"), "DDJFLX4")
        self.assertTrue(result.path("controller", "mapping").is_file())
        self.assertEqual(result.get("usb", "uuid"), "B9C8-1E1B")
        self.assertEqual(result.get("paths", "work"), "custom")
        self.assertIn("# keep this", self.path.read_text())

    def test_cancel_and_dry_run_do_not_write(self):
        before = self.path.read_bytes()
        with patch("builtins.input", side_effect=["1", "", "", "", "", "n"]):
            with self.assertRaises(Failure):
                configure(self.config)
        with patch("builtins.input", side_effect=["1", "", "", "", ""]):
            preview = configure(self.config, dry_run=True)
            self.assertEqual(preview.get("audio", "card"), "DDJFLX4")
        self.assertEqual(before, self.path.read_bytes())

    def test_overrides_stay_temporary(self):
        config = load(self.path, ["audio.card=Temporary"], env={})
        with patch("builtins.input", side_effect=["1", "", "", "", "", "y"]):
            result = configure(config)
        self.assertEqual(result.get("audio", "card"), "Temporary")
        self.assertNotIn("Temporary", self.path.read_text())

    def test_noninteractive_fails_without_writing(self):
        with patch("rx3tool.wizard.sys.stdin.isatty", return_value=False):
            with self.assertRaises(Failure):
                configure(self.config)

    def test_cli_global_path_and_start_flag_are_distinct(self):
        with (
            patch("rx3tool.wizard.configure", return_value=self.config) as wizard,
            patch("rx3tool.mapping.ensure") as mapping,
            patch("rx3tool.launch.Launcher.start") as start,
        ):
            self.assertEqual(main(["--config", str(self.path), "start", "--config"]), 0)
        wizard.assert_called_once()
        mapping.assert_called_once()
        start.assert_called_once()

    def test_setting_insert_handles_missing_final_newline(self):
        self.assertEqual(
            update_setting("[audio]\n# comment", "audio", "card", "DDJFLX4"),
            "[audio]\n# comment\ncard = DDJFLX4\n",
        )

    def test_setting_update_accepts_section_comments_and_colon(self):
        text = "[audio] # output\ncard: DDJFLX6\n"
        self.assertEqual(
            update_setting(text, "audio", "card", "DDJFLX4"), "[audio] # output\ncard = DDJFLX4\n"
        )

    def test_reselect_flx4_repairs_old_mapping(self):
        self.path.write_text("[controller]\nmidi_name = DDJ-FLX4\n")
        with patch("builtins.input", side_effect=["1", "", "", "", "", "y"]):
            result = configure(load(self.path, env={}))
        self.assertEqual(result.path("controller", "mapping").name, "Pioneer-DDJ-FLX4.rx3.xml")
