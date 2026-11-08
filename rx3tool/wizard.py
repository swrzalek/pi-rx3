"""Interactive device configuration; hardware discovery is read-only."""
import configparser
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from . import REPO
from .config import load, alsa_cards, detect_drm_cards, detect_touchscreens
from .ui import Failure, say


def choose(label, options, current, with_selection=False):
    """Options are (value, description) pairs; Enter preserves current settings."""
    say(f'\n{label} (current: {current or "none"})')
    for index, (value, description) in enumerate(options, 1):
        say(f'  {index}. {description}' + (' [current]' if value == current else ''))
    while True:
        answer = input('Choose a number (Enter keeps current): ').strip()
        if not answer:
            return (current, False) if with_selection else current
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            value = options[int(answer) - 1][0]
            return (value, True) if with_selection else value
        say('Please enter one of the listed numbers.')


def usb_choices():
    try:
        result = subprocess.run(['lsblk', '-J', '-o', 'NAME,FSTYPE,UUID,LABEL,MOUNTPOINTS,RM,TRAN'],
                                capture_output=True, text=True)
        if result.returncode:
            raise ValueError('lsblk failed')
        devices = json.loads(result.stdout).get('blockdevices', [])
    except (OSError, ValueError):
        say('Could not list music drives; keeping the current UUID is available.')
        return []
    found = []

    def walk(items, removable=False):
        for item in items or []:
            external = removable or item.get('rm') in (True, 1, '1') or item.get('tran') == 'usb'
            points = item.get('mountpoints') or []
            exported = any(p and (Path(p) / 'PIONEER/rekordbox/export.pdb').is_file() for p in points)
            uuid = item.get('uuid')
            if uuid and item.get('fstype') == 'vfat' and (external or exported):
                label = item.get('label') or item.get('name') or 'Unnamed'
                found.append((uuid, f'{label} — {uuid}' + (' (rekordbox export)' if exported else ' (FAT32)')))
            walk(item.get('children'), external)
    walk(devices)
    return found


def configure(config, dry_run=False):
    if not sys.stdin.isatty():
        raise Failure('Guided configuration needs an interactive terminal',
                      'Run ./rx3 start --config in a terminal, or use ./rx3 --set section.key=value start.')
    target = config.source or REPO / 'rx3.conf'
    # Load file values only: environment and --set must remain temporary.
    saved = load(target, env={}, allow_missing=True)
    values = {s: dict(keys) for s, keys in saved.values.items()}
    say('RX3 guided setup. Connect your controller and music USB before selecting devices.')
    say('Press Enter to keep a setting. FLX4 support is experimental.')
    try:
        profile, selected = choose('Controller', [('DDJ-FLX4', 'DDJ-FLX4 (experimental)'),
                                        ('DDJ-FLX6', 'DDJ-FLX6')],
                         saved.get('controller', 'midi_name'), with_selection=True)
        if selected:
            values['controller']['midi_name'] = profile
            values['audio']['card'] = profile.replace('-', '')
            mapping = (REPO / 'mappings/Pioneer-DDJ-FLX4.rx3.xml' if profile == 'DDJ-FLX4'
                       else saved.work / 'Pioneer-DDJ-FLX6.midi.xml')
            values['controller']['mapping'] = str(mapping)
        cards = alsa_cards()
        values['audio']['card'] = choose('Controller audio device',
            [(key, f'{key} — {card["description"]}') for key, card in cards.items()],
            values['audio']['card'])
        values['usb']['uuid'] = choose('Music USB (FAT32 rekordbox export)',
            [('', 'Start without music USB')] + usb_choices(), values['usb']['uuid'])
        displays = detect_drm_cards()
        values['display']['drm_device'] = choose('Display',
            [('auto', 'Detect automatically')] + list(dict.fromkeys(
                (c['device'], f'{c["device"]} — {c["connector"]}') for c in displays if c['panel'])),
            values['display']['drm_device'])
        values['touch']['device'] = choose('Touchscreen', [('auto', 'Detect automatically')] +
            [(t['device'], f'{t["device"]} — {t["name"]}') for t in detect_touchscreens()],
            values['touch']['device'])
        from .config import Config
        Config(values, saved.base, target).require_valid()
        say(f'\nSettings to save in {target}:')
        for section in ('audio', 'controller', 'usb', 'display', 'touch'):
            for key, value in values[section].items():
                say(f'  {section}.{key} = {value or "(none)"}')
        temporary = [f'{s}.{k}' for (s, k), origin in config.origin.items()
                     if origin.startswith('environment') or origin == '--set']
        if temporary:
            say('Temporary overrides still apply for this run: ' + ', '.join(temporary))
        if dry_run:
            say('[dry-run] Settings were not saved; mapping downloads and startup are previewed only.')
            preview = Config(values, saved.base, target)
            preview.origin = dict(saved.origin)
            for (section, key), origin in config.origin.items():
                if origin.startswith('environment') or origin == '--set':
                    preview.values[section][key] = config.get(section, key)
                    preview.origin[section, key] = origin
            return preview
        if input('Save these settings and continue? [y/N] ').strip().lower() not in ('y', 'yes'):
            raise Failure('Configuration cancelled; no settings saved and RX3 was not started')
    except EOFError:
        raise Failure('Configuration input ended; no settings saved and RX3 was not started')
    # Update only changed entries, retaining comments and unrelated settings.
    text = target.read_text(encoding='utf-8') if target.exists() else ''
    for section, keys in values.items():
        for key, value in keys.items():
            if value == saved.get(section, key):
                continue
            text = update_setting(text, section, key, value)
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(text)
    except configparser.Error as error:
        raise Failure(f'Cannot save configuration: {error}; original file preserved')
    fd, name = tempfile.mkstemp(prefix='.rx3-config-', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(text)
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    say(f'Saved {target}')
    overrides = [f'{s}.{k}={config.get(s, k)}' for (s, k), origin in config.origin.items()
                 if origin == '--set']
    return load(target, overrides)


def update_setting(text, section, key, value):
    """Preserve comments and entries outside the setting being changed."""
    import re
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if re.match(r'\s*\[' + re.escape(section) + r'\]', line)), None)
    entry = f'{key} = {value}\n'
    if start is None:
        return text.rstrip('\n') + f'\n\n[{section}]\n' + entry
    end = next((i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith('[')), len(lines))
    for i in range(start + 1, end):
        if re.match(r'\s*' + re.escape(key) + r'\s*[=:]', lines[i], re.I):
            lines[i] = entry
            return ''.join(lines)
    if end and not lines[end - 1].endswith('\n'):
        lines[end - 1] += '\n'
    lines.insert(end, entry)
    return ''.join(lines)
