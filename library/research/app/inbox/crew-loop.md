STARTED

Wire one bounded quality loop into the crew after the visual seat. Read index.html when it exists, call triggers.review if lib.triggers imports, and rerender plus recheck at most once when a hit's fix is rerender. Do not publish. Do not edit lib/render.py, lib/check.py, or lib/triggers.py. Do not call library bind, set live, or an image API.

DONE

lib/crew.py run_job calls _rerender_once after the visual seat. That reads out/index.html when the file exists and calls lib.triggers.review on that text. ImportError is a no-op. A hit whose fix is rerender runs the frontend render hand once, then the visual check_site hand once, and appends both rows. The retry is capped at one. Hits whose fix is none do not retry and do not append a row. The loop does not call library bind, does not set live, and does not call an image API. lib/render.py, lib/check.py, and lib/triggers.py were not edited. Did not publish.

py -3.14 spidercaster.py crew selftest
crew selftest ok
