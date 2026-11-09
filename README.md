# Pulchra Fellini overlay

Pulchra Fellini from Zenless Zone Zero, walking around your desktop.

Made by **gugoxiii ultimatedanx**. Their site: https://sites.google.com/view/pulchra-fellini-overlay

I'm hosting this with their permission so it builds for more than Windows. The code and art are still theirs, I'm not putting a new license on any of it.

## Version 5.2.0

Matches the author's current 5.2.0 source: seasonal holiday greetings at startup and
a "Configure Birthday..." setting (MM-DD, saved in config, default 12-15) that gets
its own greeting on the day. The new logic is ported into the shared core, so it works
on Windows, macOS and Linux. Platform adapters are unchanged, and tests cover the
birthday save/reload and the greeting selection. Download checksums are recorded in
`UPSTREAM.json`.

## Download

Grab a zip from [Releases](https://github.com/koboshchan/pulchra-fellini-overlay/releases), unzip the whole thing, and run it. You don't need Python.

| Platform | File |
|---|---|
| Windows x64 | `Pulchra.exe` |
| macOS (Apple Silicon) | `Pulchra.app` |
| Linux x64 / arm64 | `Pulchra` |

Right-click or middle-click her for the menu. Esc quits. Your settings and dialogue JSON live in your normal user config folder.

None of the builds are signed. On Mac you'll probably have to allow it in System Settings > Privacy & Security, and Windows SmartScreen might complain.

## What works where

Windows is the original and has everything: tray icon, AFK detection, click-through.

Mac and Linux run the same code (costumes, walking, dialogue, trust, timers, alarms, settings, clipboard reactions) but use the right-click menu instead of a tray icon. AFK detection and click-through are off there.

On Linux the transparent outline uses X11. If you're on Wayland, run it under XWayland, otherwise you might get a box behind her.

Heads up: like the original, it reads your clipboard locally to react to what you copy.

## Layout

`core/` has the app itself. `windows/`, `mac/` and `linux/` are the small platform bits. `pulchra.py` picks the right one.

The Mac version used to be its own older copy. It now runs the Windows code.

## From source

Python 3.12 with Tk.

```sh
pip install -r requirements.txt
python pulchra.py
```

On Debian/Ubuntu you'll need `python3-tk` first.

To build it yourself:

```sh
pip install -r requirements-build.txt
python build.py
```

Actions builds all four targets on every push, and a `v*` tag puts them in a release. The original author's notes are in `UPSTREAM-README.txt`.
