# Grok Imagine test — 2026-10-01 13:39 local, before 16:00

Provider `xai`, model `grok-imagine-image-2.0`, quality `low`, resolution `1k`.
Key file was the SGH Console key. The receipt JSON stores no key and no provider URL.
The page favicon is still the built SVG. These PNGs are tests, not a publish.

## What held

- All four calls returned bytes. No text or watermark landed in the pictures.
- `floelixir-hero.png` is the one to keep. Cup, steam, notebook, morning window. It matches the ritual brief and still reads if the hero is short.
- `movelixir-mark.png` followed a flat-icon prompt: one cream M on plum. Usable as a mark study. The live favicon stays the SVG, which stays sharp at 16px.

## What to change in the next prompt

- Say "subject on the right third, quiet space on the left" when the desktop hero is a split. `movelixir-hero.png` centers the walker, so a side-by-side crop fights him.
- Say "no identifiable face" or "seen from behind" unless a real person was supplied. The move and recovery heroes invented people.
- For a 168px-tall phone hero, ask for a tighter, brighter subject. `recovelixir-hero.png` is a good room and a dim face. At phone height the lamp wins and the person almost disappears.
- "Resting" became "asleep." If the page is about a ritual rather than sleep, say "awake, eyes open, sitting."
- Do not ask the photo model for a 16px favicon. Ask it for heroes. Keep the letter mark in `favicon.svg`.
