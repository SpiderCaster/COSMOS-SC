DONE 2026-10-01 13:59:53

render, before assemble: if the homepage hero has no usable local image, and the project contains assets/hero.png, assets/hero.jpg, assets/hero.jpeg, or assets/hero.webp (first that exists, in that order), it sets the hero src to assets/hero.<ext> and a non-empty alt from the hero heading or the site name. It copies those bytes to <out>/assets/hero.<ext>. Remote srcs, paths containing `..`, and paths that resolve outside the project are rejected. If no local hero file exists, the letter mark is left alone. asset_list reports assets/hero.<ext> and still fails remote URLs.

py -3.14 -m lib.hands.selftest
hands selftest ok
