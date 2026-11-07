# Install

Windows runs SpiderCaster-Setup.exe from the download page on this site.
The wizard does not need an administrator. Its shortcut opens the studio.

Other systems clone SpiderCaster / COSMOS-SC from GitHub and run it with Python.

- Run SpiderCaster-Setup.exe on Windows.
- git clone the SpiderCaster / COSMOS-SC repository
- cd COSMOS-SC
- python spidercaster.py build projects/demo-local --offline --out sites/demo-local
- python spidercaster.py check sites/demo-local
- python spidercaster.py serve sites/demo-local
- Nothing publishes until you copy the built files to a host yourself.
