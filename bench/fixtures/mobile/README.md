# Mobile gate fixtures (bench\mobile_bench_selftest.py)

Each bad page breaks exactly one gate; `clean.html` must pass every gate at every viewport.

| Fixture | Breaks | How |
|---|---|---|
| clean.html | nothing | viewport meta, 18px copy, working nav toggle, 48px controls, raster img with srcset+sizes |
| overflow.html | overflow_x | a 600px-wide strip (fails at 360/390/412, fits at 1280) |
| tap30.html | tap_target_rendered | a 30px-tall button |
| text12.html | type_floor_rendered | body font-size 12px |
| no_viewport.html | viewport_meta | no `<meta name="viewport">` |
| grey_tile.html | grey_tile_rendered | `.hero-photo` flat #ccc box with no image + an img whose file 404s |
| nav_broken.html | nav_toggle | menu button with no script: aria-expanded never flips (mobile only; nav is inline at 1280) |
| nav_clipped.html | nav_toggle | menu opens (aria-expanded flips) into a fixed 26px-tall strip, so 48px links are cut off (mobile only) |
| sticky_tall.html | sticky_25 | sticky bar at 40vh |
| img_nosrcset.html | img_srcset | raster img without srcset |

photo-320.png / photo-640.png are generated gradients (no external images).
