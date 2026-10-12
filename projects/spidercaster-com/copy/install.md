# Two clicks to install

You need Python 3.11 or newer. Nothing else.

1. Get the folder from GitHub: SpiderCaster/COSMOS-SC
   (click one: download or clone).
2. Double-click Start-SpiderCaster.cmd on Windows, or run
   ./start-spidercaster.sh on Unix (click two). The doctor checks the setup,
   the demo builds at zero tokens, and the studio desk opens in your browser.

The desk has rooms for the plan, the paint, the check, and the preview. Nothing publishes from here. Publish stays a command a person runs.

To rehearse with no side effects first:

- python spidercaster.py start --dry-run runs doctor only. No writes, no server, no browser.
- python spidercaster.py doctor prints a JSON report. "ok": true means the molds, frames, seats, and hands line up.
