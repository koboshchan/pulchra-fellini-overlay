README

CURRENT VERSION : 5.2.1
Approx work time ~ 33hrs

Current major version release notes

-Added more seasonal and regional holidays
-Added seasonal holiday awareness and birthday configuration 5.2.0
-Fixed a bug where the shortcut did not save 5.1.1
-Added a headpat shortcut you can assign so that you can quickly change settings 5.1.0
-Fixed a compiling error in the exe version 5.0.1
-5.0.0 Changed the walk assets with a spritesheet and added more frames 5.0.0
-Added a custom anchor point 4.2.0
-Fixed a trust obfuscation bug 4.1.5
-Fixed a quote pull bug 4.1.4
-Fixed a trust glitch 4.1.3
-Added a reset settings option 4.1.2
-Fixed a bug in the trust meter 4.1.1
-Added a trust meter 4.1.0
-Fixed a threading bug 4.0.4
-Fixed a bug where click irritation did not work for some costumes
-Reworked the casual costume 4.0.2
-Added a quote fallback for the new costumes 4.0.1
-Added 2 new costumes!!! 4.0.0

Older versions are shown in the end



Instructions / prerequisites

1a: If python is already installed, skip steps 1b-2
1b: Download Python from https://python.org and open the installer.
2: Make sure to check the box that says "Add python.exe to PATH" before installing.
3: Open command prompt or your IDE. If using IDE, open the terminal
4a: Type "pip install Pillow pystray tkinterdnd2 psutil" in the terminal. This is a critical step.
5: Extract this ZIP folder, then double-click your script to run it.



Controls and Shortcuts

Move: Left-click and hold anywhere on the character to drag her around. Note that clicking her has a 25% chance to trigger an interactive dialogue response instead of dragging. Flicking her fast across the screen causes her window to shake on impact.
File Inspector: Drag and drop files from Windows straight onto her frame to get customized text reactions based on the file type.
Menu: Right-click or middle-click the character or system tray icon to open the menu.
Exit: Press "Esc" key on your keyboard to close the overlay instantly.

-If you would prefer to change the image, you can add files with .png , .jpeg , .bmp , and .gif files. .gif files will remain motionless. SUpport for animations may be added later .jpeg pictures will not have a transparent background, as they do not support it

-The .ico file is an icon you can use for a shortcut on your desktop, or you can supply one inside the directory to change the taskbar tray appearance.

-The .bat file should be configured for the correct path to function as a launcher



Advanced Menu Functions

-Open settings dashboard : opens advanced settings

-Select costume: Changes the image layout. Fully configurable inside the script files.
-Scale size: Adjusts the relative scale sizing of the character on your screen.
-Snap to Node: A sub-menu to instantly teleport her flush against any of the 8 screen grid points.
-Send to Bottom Right: Instantly zips her straight back to her default home base coordinate tracking.
-Snap to Nearest Node: Measures her coordinates and magnetizes her flush to the nearest edge boundary.
-Walk to Node: A sub-menu that commands her to actively walk and glide along the screen borders to any of the 8 grid positions with custom walking animations.
-Drag Lock: Pins the companion in place on your screen layout so she cannot be dragged accidentally.
-Click-Through: Makes her character completely phantom to mouse inputs. Clicks pass straight onto windows underneath.
-Flip Direction: Mirrors the image layout horizontally to change which direction she is facing.
-Opacity: Fades her background transparency down across 25%, 50%, or 75% depth tiers.
-Open Folder Path: Launches Windows Explorer straight into her active script directory folder path.
-Toggle Chat Bubbles: Turns randomized environmental commentary on or off.
-Toggle Auto-Costume Swap: Enables or disables the background script routine that randomly changes her clothing and expressions every 15 minutes.
-Toggle Edge Patrol Walks: Toggles her autonomous perimeter exploration mode, allowing her to pick a random screen node and walk to it every 5 minutes when idling.
-Get Intel: Skips the active chat generation cooldown and resets her internal discussion timer loops.
-Alarm Options: Allows you to lock in a specific time of day (Must use strict 24-hour HH:MM notation, e.g., 16:30) to trigger a persistent warning banner that stays pinned over her frame until manually clicked to clear.
-Start Contract Timer: Launches a countdown timer. Pick a quick pre-set or choose "Set Custom Timer..." to input custom minute values. Once complete, it deploys an infinite holding alert banner.
-Toggle Resource Monitor: Watches your background system. Drops warning bubbles if CPU/RAM load crosses 85%, or if unplugged laptop battery percentages fall underneath 50%.
-System Pulse Check: Runs an on-demand hardware snapshot to display current CPU load, RAM usage, and upload/download network speeds in a visual message block.
-DVD bouncing mode : works like the classic dvd screensaver


Ways to earn Trust:
• Daily Login Bonus (+10 Points): Booting up the companion for the first time each calendar day pays a contract dividend. (Capped strictly at once per day to prevent restart exploits).
• Complete Contract Timers (+10 Points): Successfully staying focused and letting a 5-minute, 25-minute, or 1-hour contract countdown timer reach zero cleanly.
• Waking Up On Time (+5 Points): Setting a custom 24-hour alarm and manually clicking the persistent pop-up bubble to dismiss it when it triggers.
• Secure File Transfer (+3 Points): Dropping verified asset categories directly onto her window (e.g., source scripts, notes, images, compressed archives, or recognized character keyword files).
• System Metrics Audit (+1 Point): Actively checking system health telemetry by clicking System Pulse Check via the system tray or context layout menu.
• Gathering Intel (+1 Point): Forcing manual communication check-ins by choosing the Get Intel command.

You will lose trust by:
• Extreme Cursor Irritation (-8 Points): Continuously poking or dragging her window 7+ times in a short window. This snaps her irritation engine, forces an immediate 8-point penalty, and causes her to vanish to a random monitor corner.
• The Trust Freeze Guard: Activating the Pause Trust Meter switch inside the configuration dashboard completely freezes all point increments and penalties.
• The Performance Cap (200 Max): Trust points top out securely at a hard ceiling of 200 points to prevent variable overflows or interface breaks.


Required Image Asset Directory

For the costumes and animations to cycle properly, the following exact filenames must exist within the active directory folder layout alongside the script:
pulchra_overlay_standing.png
pulchra_overlay_sitting.png
pulchra_overlay_action_1.png
pulchra_overlay_action_2.png
pulchra_overlay_thinking.png
pulchra_overlay_tail.png
pulchra_overlay_casual.png
pulchra_overlay_burnt.png
pulchra_overlay_icon.ico

Perimeter Patrol Animation Strips:
pulchra_walk_spritesheet.png



Profiles & Configs

config.json: Automatically generated upon changes. Holds coordinate tracking data, window sizing scales, opacity depth states, and menu choices to carry profiles over across workstation restarts.
mood_quotes.json / costumes.json: Text libraries storing her dialogue strings. Feel free to open these directly to customize her personality pool!



System Performance requirements

-CPU Requirement: ~0% at idle. Briefly blips up only during pathing loops or mouse dragging events.
-RAM Requirement: ~35 MB – 70 MB total (Varies slightly based on active costume asset resolution and size scaling choices).
-GPU Requirement: 0%. No dedicated or integrated graphics hardware parameters required.



Troubleshooting

-Make sure your companion image files stay inside the exact same folder as the script profile.
-Ensure you fully extract all files completely out of the compressed ZIP archive folder layout before attempting execution.
-If she fails to launch entirely, reinstall your Python core engine and double-check that the "Add python.exe to PATH" checkbox configuration is filled.
-If you activate Click-Through and can no longer right-click her frame directly, locate her context settings using the active system tray taskbar icon layout. (If hidden, select the Windows hidden items '^' arrow to drag her icon to the visible taskbar tray area).
-If the Resource Monitor won't activate, the System Pulse Check fails, or Drag-and-Drop file inspection triggers terminal crash codes, verify that all prerequisites listed under Step 4a were successfully installed without network restrictions.
-If dialogue text windows look blank or format poorly, verify that custom edits inside your automatically generated "quotes.txt" or "costumes.json" layouts don't contain broken punctuation markers or empty lines.


Maybe next features I guess idk

total click count
seasonal awareness
maybe window awareness

Legacy versions changelog


-Added a light mode for chat bubbles 3.6.0
-Added a cooldown editor 3.5.0
-Added a section into the code to accomodate hi-res icon assets 3.4.5
-Fixed a walking bug 3.4.4
-Changed the quote source names for easier distinction 3.4.3
-Fixed critical runitme bugs 3.4.2
-Fixed slightly to allow exe compiling 3.4.1
-Added a funcion to disable edge snapping 3.4.0
-Fixed a costume swapping bug when exiting dvd mode 3.3.1
-Added a dvd bouncing mode 3.3.0
-Made walking animations slighlty more natural 3.2.3
-FIxed critical perf bugs in the exit afk function 3.2.2
-Added a shaking animation when returning from afk 3.2.1
-Added a afk state tracker 3.2.0
-Fixed a dragging bug 3.1.1
-Added an irritability function to when she is clicked 3.1.0
-Fixed a few performance bugs 3.0.2
-Added smart clipboard reactions 3.0.1
-Bug fixes and imporvements 3.0.6
-Added an option to open the settings menu from the system tray 3.0.5
-FIxed a few bugs in the code 3.0.4
-Fixed the walk cancel quotes to make them more natural 3.0.3
-Fixed auto quotes.txt file generation 3.0.2
-FIxed the mood selection bug 3.0.1
-Added a dedicated settings window, and finally added mask-less costumes! 3.0.0
-Fixed critical threading bug 2.6.20
-Fixed critical costume swapping bugs 2.6.19
-Fixed a bug in the walking functions 2.6.18
-FIxed the time-sensitive comments time definitions 2.6.17
-FIxed a missing .png extension 2.6.16
-Fixed a duplicate function 2.6.15
-Fixed a severe threading bug 2.6.14
-Removed a duplicate  def block in the code 2.6.13
-Fixed network test bug 2.6.12
-Changed the auto costume swap cooldown 2.6.11
-Added a cancel walk animation function 2.6.10
-Added more file-drop reactions 2.6.9
-Fixed one of the walking costumes 2.6.8
-Made walking animations less goofy 2.6.7
_Fixed a bug where she switched back to her default costume after walking 2.6.6
-Fixed a bug where settings were not saved on exit 2.6.5
-Removed duplicate def blocks 2.6.4
-Added mid walking animation frames 2.6.3
-Fixed duplicate def code 2.6.2
-Added "walk to node" function 2.6.1
-Added walking mechanics, she will now walk to a different coner every 5 mins 2.6.0
-Added a second action costume 2.5.4
-Fixed system tray menu bug 2.5.2 and 2.5.3
-Added persisten chat bubble for timers 2.5.1
-Added alarm clock functionality 2.5.0
-Fixed chat box text color 2.4.4
-Slightly changed the chatbox color 2.4.3
-Added an extrnal quotes library for specific costumes 2.4.2
-Removed processor temp due to system blocks 2.4.1
-Fixed a network speed test bug in the pulse check 2.4.1
-Added time-reactive messages 2.4.0
-Older changes (2.4.0 and older) are not shown because of lack of version monitoring before