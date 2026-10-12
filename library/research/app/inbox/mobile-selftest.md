STARTED

Mobile selftest for the SpiderCaster renderer. Builds a tiny temp site through the same plan_offline then render.assemble path as lib/regress.py. Asserts live in lib/mobile_selftest.py. Do not publish. Do not edit lib/render.py. No --live. No secrets.

DONE

lib/mobile_selftest.py builds a temp project and calls plan_offline, then render.assemble. Waited 2 minutes, then ran the selftest. The module retried once after 60 seconds. Asserts were not weakened. That run is the result below. Did not publish. Did not edit lib/render.py. No --live. No secrets.

Set-Location '<repo-root>'; py -3.14 -m lib.mobile_selftest
missing aspect-ratio:16/9
still present height:168px
still present about-panel
exit 2

