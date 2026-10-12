STATUS: STARTED 2026-10-01

Index check in lib/check.py, beside the other phone rows. No class="phone-bar" adds no phone_bar row. A CSS .phone-bar rule is not that class. When one or more phone-bar links are present, every href must start with tel: and the digits in that href must equal the digits in the link text. A leading + in the href is allowed and is not a digit. Fewer than 7 digits is phone_bar FAIL. A matching bar is phone_bar PASS. A bad bar is phone_bar FAIL. Existing asserts were not weakened. lib/render.py, lib/offline.py, lib/crew.py, lib/triggers.py, stage/, and seat files were not edited. No publish. No --live.

STATUS: DONE

py -3.14 -m lib.hands.selftest
hands selftest ok

py -3.14 spidercaster.py crew selftest
crew selftest ok
