# Two clicks to install

One command fetches the SpiderCaster build from its hosted download,
checks the file's checksum, and leaves a starter on your machine.
Windows needs nothing else. macOS and Linux need Python 3.11 or newer.

Windows (PowerShell, click one):

  irm https://mdata.tokenctr.com/spidercaster/install.ps1 | iex

macOS or Linux (click one):

  curl -fsSL https://mdata.tokenctr.com/spidercaster/install.sh | sh

Click two: double-click Start-SpiderCaster.cmd on Windows, or run
start-spidercaster.sh on Unix. The doctor checks the setup,
the demo builds at zero tokens, and the studio desk opens in your browser.

The desk has rooms for the plan, the paint, the check, and the preview. Nothing publishes from here. Publish stays a command a person runs.

To rehearse with no side effects first:

- python spidercaster.py start --dry-run runs doctor only. No writes, no server, no browser.
- python spidercaster.py doctor prints a JSON report. "ok": true means the molds, frames, seats, and hands line up.
