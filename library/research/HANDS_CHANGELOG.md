# Hands changelog

Date: 2026-10-01. No new public hand. `ROLES` and `HANDS` keys are unchanged.

## Local homepage hero

A project may contain `assets/hero.png`, `assets/hero.jpg`, `assets/hero.jpeg`, or `assets/hero.webp`. First file that exists wins, in that order. The src written on the hero is the relative path `assets/hero.<ext>`.

The file must sit inside the project directory. Reject a resolved path that escapes the project, any path containing `..`, and any src that starts with `htt<local-path>`, `https://`, or `//`.

`render` checks this before `assemble`. If the homepage hero has no usable local image and one of those files exists, it sets that relative src and a non-empty alt from the hero heading, or `<site name> hero` when the IR has a name and no heading. It copies the file bytes to `<out>/assets/hero.<ext>` and does not rewrite the image. If none of those files exist, the letter mark stays. A remote, `..`, absolute, or escaping src is cleared so it is not emitted.

`asset_list` adds `assets/hero.<ext>` to `data.local` when that file exists. Remote asset URLs still FAIL.

Selftest (`py -3.14 -m lib.hands.selftest`) printed:

```
hands selftest ok
```
