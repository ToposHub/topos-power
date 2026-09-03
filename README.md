# Topos Power

[中文](README.zh-CN.md) | **English**

Topos Power is a cross-platform power timer built with PyQt6. It supports:

- Scheduled shutdown
- Scheduled sleep
- Display-only sleep
- Turning off the display before sleep
- Reading and editing macOS/Windows idle display/sleep settings
- Preventing automatic system sleep during a countdown
- Animated circular progress, power phase timeline, and subtle breathing effects
- Instant Chinese and English interface switching

## Screenshots

<p align="center">
  <img src="assets/screenshots/scheduled-shutdown.png" alt="Scheduled shutdown interface" width="48%">
  <img src="assets/screenshots/scheduled-sleep.png" alt="Scheduled sleep interface" width="48%">
</p>

## Project structure

```text
Topos Power/
├── src/topos_power/
│   ├── app.py                 # Application entry point
│   ├── config.py              # Application name and version
│   ├── core/localization.py   # Chinese and English interface text
│   ├── core/power_manager.py  # Cross-platform power operations
│   └── ui/                    # Qt interface, widgets, and styles
├── tests/                     # Automated tests
├── pyproject.toml
└── requirements.txt
```

## Usage guide

### Scheduled shutdown

1. Select **Schedule Shutdown**.
2. Drag the execution-time slider to choose the countdown duration.
3. Review the estimated shutdown time and click **Start countdown**.
4. To cancel a scheduled shutdown, click **Stop task** before the countdown finishes.

### Scheduled sleep

1. Select **Schedule Sleep**.
2. Choose one of the available modes:
   - **System sleep**: put the computer to sleep when the countdown ends.
   - **Turn off display**: turn off the display while keeping the computer running.
   - **Display, then sleep**: optionally lock the screen, turn off the display early, and enter sleep at the end of the countdown.
3. Enable **Prevent auto-sleep** if the countdown must continue without being interrupted by the system's idle sleep timer.
4. On macOS and Windows, the system idle display/sleep settings can be reviewed in the settings card shown in sleep mode.

### System idle settings

These settings control what the operating system does after a period of keyboard/mouse inactivity. They are different from Topos Power's one-time countdown:

- **Display** controls when the display turns off.
- **Sleep** controls when the computer enters system sleep.
- `0` means **Never**.
- On Windows, the displayed values are from the active power plan's plugged-in profile. Saving synchronizes both plugged-in and battery profiles.

## Platform support

| Capability | macOS | Windows | Linux | Notes |
| --- | :---: | :---: | :---: | --- |
| Scheduled shutdown | ✓ | ✓ | ✓ | Uses the native shutdown scheduler |
| Scheduled system sleep | ✓ | ✓ | ✓ | Uses the operating system sleep command |
| Turn off display | ✓ | ✓ | ✓ | Keeps the computer running |
| Lock screen before action | ✓ | ✓ | ✓ | Uses the native lock-screen mechanism |
| Prevent countdown auto-sleep | ✓ | — | — | Currently implemented through macOS `caffeinate` |
| Read idle display timeout | ✓ | ✓ | — | Linux desktop APIs are not unified |
| Read idle sleep timeout | ✓ | ✓ | — | Linux desktop APIs are not unified |
| Write idle display timeout | ✓ | ✓ | — | Windows writes both AC and battery profiles |
| Write idle sleep timeout | ✓ | ✓ | — | `0` means Never |
| Chinese / English interface | ✓ | ✓ | ✓ | Saved locally for the next launch |
| System tray operation | ✓ | ✓ | ✓ | Depends on desktop tray support |

### Native system adapters

| Platform | Shutdown | Sleep | Display off | Lock screen | Idle settings |
| --- | --- | --- | --- | --- | --- |
| macOS | `shutdown` via AppleScript | System Events | `pmset displaysleepnow` | System Events | `pmset -g` / `pmset -a` |
| Windows | `shutdown.exe` | `SetSuspendState` | `SC_MONITORPOWER` | `LockWorkStation` | `powercfg /query` / `powercfg /change` |
| Linux | `shutdown` | `systemctl suspend` | `xset` / `xdg-screensaver` | `loginctl` / desktop tools | Desktop-specific; not enabled yet |

### Countdown modes

| Mode | At countdown end | Optional steps | Typical use |
| --- | --- | --- | --- |
| Scheduled shutdown | Shuts down the computer | Lock screen | Long-running task cleanup |
| System sleep | Enters system sleep | Lock screen | Pause work and save power |
| Display-only | Turns off the display | Lock screen | Keep downloads or services running |
| Display, then sleep | Turns off the display early, then sleeps | Lock screen, early display-off offset | Reduce screen power while keeping a predictable sleep time |

Linux desktop environments expose idle power settings through different APIs. The core actions remain available, while the unified idle-settings panel is intentionally hidden until a reliable GNOME/KDE/Xfce strategy is available.

## Design overview

Topos Power keeps the interface, localization, and operating-system commands separate:

```text
Qt interface
    ├── countdown state and animated widgets
    ├── Chinese / English localization
    └── user actions
             │
             ▼
PowerManager platform adapter
    ├── macOS: pmset / AppleScript / caffeinate
    ├── Windows: shutdown / powercfg / Windows API
    └── Linux: systemctl / xset / desktop-session commands
```

The countdown is handled by the Qt event loop, while potentially blocking system operations run in background threads. The circular progress and phase timeline provide visual feedback without changing the underlying power commands.

## How to run

### Method 1: One-click launch scripts

On macOS, double-click `run_topos.command` in the project root. If macOS blocks the script, run it from Terminal:

```bash
./run_topos.command
```

On Windows, double-click `run_topos.bat` in the project root.

Both scripts prefer the project's `.venv` and support the `src` layout automatically.

### Method 2: Traditional Python launch

```bash
cd "Topos Power"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m topos_power
```

You can also install the command-line entry point:

```bash
topos-power
```

## Interface languages

Use the language selector in the top-right corner to switch between Chinese and English. The choice is applied immediately and saved locally for the next launch.

## License and copyright

Copyright (C) 2026 ToposHub

Topos Power is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See [LICENSE](LICENSE) for the complete license text. The software is provided “as is”, without warranty of any kind.

When distributing modified or packaged versions, retain the copyright notice, license text, and third-party notices, and provide the corresponding source code as required by GPL-3.0-or-later.

Topos Power depends on PyQt6. The PyQt6 community version is licensed under GPLv3. Distributions that include PyQt6, Qt, or other third-party components must comply with the licenses that apply to those exact components. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting contributions.

## Run tests

```bash
pytest
```

For development, install the project in editable mode with `pip install -e .`, then run the test suite after changing the power manager, localization, or UI code.

## Platform notes

- macOS uses `pmset` and AppleScript for power operations and idle settings. The first use may require an administrator password.
- Windows uses the built-in `powercfg` command for the active power plan. The idle settings panel synchronizes the plugged-in and battery values.
- Linux supports the core power actions through available desktop/system commands. Idle display/sleep settings are not exposed yet because GNOME, KDE, Xfce, and other desktop environments use different configuration APIs.
- Lock-screen operations may require additional operating-system permissions.

## Design principles

Power operations are separated from the Qt interface. System command results are returned to the interface so failed operations are not shown as successful. On macOS, display sleep uses `pmset displaysleepnow` and does not modify display gamma settings.
