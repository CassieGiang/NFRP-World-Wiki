# Reporting bugs
How to send a bug report with your log, so it can be found and fixed.

@@summary Right after the bug, before restarting, take your Player.log and open a bug report on GitHub: say what happened, how to make it happen, and drag the log in. The log is public there and holds your Windows user name.

## 1. Keep the log
- Right after the bug, **before you restart the game**. Restarting starts a new log, and the old one moves to Player-prev.log.
- Note what you did and what happened while you still remember it. A screenshot or a short video helps a lot with animations and effects.

## 2. Find Player.log
- **Windows:** press Win+R, paste **%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios** and press Enter.
  - RimWorld 1.6: **Player.log** is in that folder.
  - RimWorld 1.7: it is in the **Logs** folder inside it.
- **Already restarted?** Send **Player-prev.log** from the same folder: that is the log from before.
- **Mac and Linux** (RimWorld 1.6): the RimWorld by Ludeon Studios folder is under ~/Library/Logs/Ludeon Studios (Mac) or ~/.config/unity3d/Ludeon Studios (Linux). On 1.7, look for a Logs folder in the game's save-data folder.

## 3. Open a bug report
- Open [a new bug report](https://github.com/CassieGiang/NFRP-World-Wiki/issues/new?template=bug_report.yml). You need a free GitHub account.
- Fill in what happened and how to make it happen, then **drag Player.log into the log box**. If GitHub says the file is too large, zip it first.
- Pick your RimWorld version and how big your mod list is. Bugs that also happen with only the required mods are the quickest to fix.
- **Your log is public there.** It shows your Windows user name in file paths and lists your mods. If you'd rather not share that, remove the user name with a text editor first, or ask in the Workshop comments for another way.

## What makes a good report
- **One bug per report.** Two bugs in one report get mixed up.
- **Name the technique, item or event** exactly as the game shows it, e.g. "Katon: Gōkakyū no Jutsu (Fire Release: Great Fireball)".
- **Say whether it happens every time** or only once.
- Seen a report for the same bug already? Add your log there instead of opening a new one.
