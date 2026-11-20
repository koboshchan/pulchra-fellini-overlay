# Pulchra Fellini overlay

Pulchra Fellini from Zenless Zone Zero, walking around your desktop.

Made by **gugoxiii ultimatedanx**. Their site: https://sites.google.com/view/pulchra-fellini-overlay

I'm hosting this with their permission so it builds for more than Windows. The code and art are still theirs, I'm not putting a new license on any of it.

## Version 6.0.0

Tracks upstream 6.0.0, which adds an optional in-character AI chat ("Open Comms").
This fork implements it inside the app instead of bundling upstream's separate
closed `pulchra_chat.exe`.

**Privacy.** The AI chat is OFF by default and Pulchra makes no network requests
of its own before you opt in. To use it, open *Open Comms (AI Chat)* from the
right-click menu (or head-tap shortcut), tick *Enable AI chat*, accept the
disclosure, and enter your own service address, model and API key. After that,
each message you press Send on is sent to that service together with Pulchra's
character prompt (`assets/pulchra_prompt.txt`) and your last few chat turns.
Nothing else from your computer is sent. No API key is bundled. Your key is saved
in plain text in `ai_chat.json` in the settings folder (mode 600 where
supported), or set the `PULCHRA_AI_API_KEY` environment variable instead. Only
https addresses are accepted, or http on your own computer. Any
OpenAI-compatible chat completions service works.

Costume/heart fixes, native transparency, saved cooldowns, Flip Gravity and all
other fork features are unchanged. Upstream's note that the app is fully offline
no longer applies once you enable AI chat. Checksums and notes are in
`UPSTREAM.json`.

## Download

Grab a zip from [Releases](https://github.com/koboshchan/pulchra-fellini-overlay/releases), unzip the whole thing, and run it. You don't need Python.

Use these releases to update this cross-platform fork. The author's new Windows
installer downloads their upstream app, not these builds; it is not bundled
or used here.

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
