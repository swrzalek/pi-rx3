# Stop Desktop Before RX3 Implementation Plan

**Goal:** Add explicit `start --stop-desktop` to release the graphical display.

**Architecture:** After normal preflight checks and under the launcher lock, stop display-manager through the existing sudo helper before starting RX3. Reject graphical terminals; permit SSH and text consoles. No boot configuration is changed. Print the desktop restoration command.

**Tech Stack:** Python standard library, systemctl, unittest.

- [ ] Add CLI flag and conditional launcher invocation, keeping normal start unchanged.
- [ ] Add session checks, systemctl discovery and desktop stop method in launch.py.
- [ ] Test graphical rejection, SSH/console operation, failure and dry-run behavior with mocked processes.
- [ ] Document logout and restoration behavior, run focused tests and review.
