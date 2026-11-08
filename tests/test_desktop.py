"""Desktop release must preserve the controlling session and respect dry runs."""
import os
import subprocess
import unittest
from unittest.mock import patch
from rx3tool.config import load
from rx3tool.launch import Launcher
from rx3tool.ui import Failure
from rx3tool.cli import main


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.launcher = Launcher(load(env={}))

    def test_graphical_terminal_is_rejected(self):
        with patch.dict(os.environ, {'WAYLAND_DISPLAY': 'wayland-0'}, clear=True), \
             patch.object(self.launcher, 'sudo') as sudo:
            with self.assertRaises(Failure):
                self.launcher.stop_desktop()
            sudo.assert_not_called()

    def test_console_and_ssh_stop_display_manager(self):
        for env in ({}, {'SSH_CONNECTION': 'remote', 'DISPLAY': ':0'}):
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True), \
                 patch('rx3tool.launch.shutil.which', return_value='/usr/bin/systemctl'), \
                 patch.object(self.launcher, 'sudo', return_value=subprocess.CompletedProcess([], 0)) as sudo:
                self.launcher.stop_desktop()
                sudo.assert_called_once_with(['systemctl', 'stop', 'display-manager.service'],
                                             check=False, capture=True)

    def test_service_failure_is_actionable(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch('rx3tool.launch.shutil.which', return_value='/usr/bin/systemctl'), \
             patch.object(self.launcher, 'sudo', return_value=subprocess.CompletedProcess([], 1, '', 'denied')):
            with self.assertRaisesRegex(Failure, 'Could not stop'):
                self.launcher.stop_desktop()

    def test_dry_run_does_not_execute_systemctl(self):
        self.launcher.dry_run = True
        with patch.dict(os.environ, {}, clear=True), \
             patch('rx3tool.launch.shutil.which', return_value='/usr/bin/systemctl'), \
             patch('rx3tool.launch.subprocess.run') as run:
            self.launcher.stop_desktop()
            run.assert_not_called()

    def test_cli_flag_reaches_launcher(self):
        with patch('rx3tool.launch.Launcher.start') as start:
            self.assertEqual(main(['start', '--stop-desktop', '--dry-run']), 0)
        start.assert_called_once_with(stop_desktop=True)
