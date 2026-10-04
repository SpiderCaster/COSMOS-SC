STARTED
2026-10-01
Task: hero primary button names and links the next section with a non-empty title. Do not use the first three words of the subhead. Do not point at an empty-title about section. If no titled section exists, omit the primary button. No publish. No --live. No --frame. Do not edit projects/.

restage-demo3.md already contained DONE on the first read. Did not wait out the 8 minutes.

DONE
2026-10-01
plan_offline sets the hero primary from the next section with a non-empty title. The label is that title. The href is # plus that section id. An empty-title about section is skipped. The first three words of the subhead are not used. If no titled section exists, the primary button is omitted.

Did not publish. Did not pass --live. Did not pass --frame. Did not edit projects/. Did not add a hero image. stage/harbor/src and stage/demo/src were already present.

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok

py -3.14 spidercaster.py crew run stage\harbor\src --site harbor-test.example --out stage\harbor\out --mold discover-grid
exit 0. Mold discover-grid. No frame. 0 local assets.

py -3.14 spidercaster.py crew run stage\demo\src --site demo-stage.example --out stage\demo\out --mold clarify-mix
exit 0. Mold clarify-mix. No frame. 0 local assets.

Harbor primary button: "Contact" href="#contact". That id is on the page as <h2>Contact</h2>. Not "A quiet tea". Not #about.

Demo primary button: "Build" href="#features". That id is on the page as <h2>Build</h2>. Not "Read on". Not a sliced sentence.
