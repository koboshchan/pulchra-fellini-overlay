# Pulchra Fellini overlay

A desktop companion featuring Pulchra Fellini from Zenless Zone Zero.

Original author: **gugoxiii ultimatedanx**. Original project and support site:
https://sites.google.com/view/pulchra-fellini-overlay

This repository is published with the original author's permission, as confirmed
by the repository owner. It maintains the author's Windows 5.1.1 source with
cross-platform packaging. No new license is asserted over the original code or
artwork; those rights remain with their respective owners.

## One shared application

The newer Windows version is canonical. Mac now matches Windows in shared
application logic and content, including costumes, spritesheet walking, dialogue,
trust, timers, alarms, settings and clipboard reactions. The outdated separate
Mac application is not used.

All application logic lives in `core/`. Small adapters in `windows/`, `mac/`
and `linux/` implement the platform interface. The single `pulchra.py` entry
point selects the appropriate adapter. All four CI targets build that same code.

## Download and run

Download an artifact from the Actions tab, or an archive from Releases. Extract
the entire archive before running Pulchra. Python is not needed for packaged
builds. Windows provides Pulchra.exe; Linux provides Pulchra; Mac provides
Pulchra.app.

Right-click or middle-click the pet for controls and About / Credits. Escape
exits. Configuration and editable dialogue JSON are stored in your user config
directory, not inside the executable or a temporary extraction directory.

## Platform differences

Windows retains the original tray icon, system-wide AFK detection and click-through.
Mac uses native Tk transparency. Linux uses X11 SHAPE for the character outline,
including walking frames. XWayland is recommended on Wayland desktops; native
Wayland support is not guaranteed and may show a rectangular background.

Mac and Linux currently use the pet's context menu instead of a tray icon.
System-wide AFK detection and click-through are Windows-only and are safely
disabled elsewhere. This avoids requiring input-monitoring permissions or leaving
a click-through pet with no recovery controls. Core features and content are
shared, but these native integrations are not yet equivalent.

Mac builds are unsigned and not notarized. Gatekeeper may require approving the
download in System Settings. Windows builds are unsigned too and may trigger
SmartScreen. CI smoke tests verify startup and basic operations, not a complete
interactive desktop acceptance test.

The original app reads clipboard text locally for reactions. File drops inspect
names/extensions. Review the source if these features matter to your privacy.

## Run from source

Use Python 3.12 with Tcl/Tk installed.

```sh
python -m pip install -r requirements.txt
python pulchra.py
```

On Debian/Ubuntu, install `python3-tk` and X11 libraries first.
For a headless startup test on Linux:

```sh
xvfb-run -a python pulchra.py --smoke-test
```

## Build

```sh
python -m pip install -r requirements-build.txt
python build.py
```

GitHub Actions builds Linux x86_64, Linux arm64, Windows x86_64 and macOS arm64
on every push. Tags matching `v*` also publish all four archives to a release.
The Linux builds target Ubuntu 24.04 or compatible newer glibc systems.
See UPSTREAM-README.txt for the original author's detailed feature notes.
