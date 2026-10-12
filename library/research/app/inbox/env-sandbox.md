# env-sandbox

STATUS: DONE 2026-10-01 14:42:04

Was STARTED, then written after lib/sandbox.py was on disk.

Wrote:
- library/resources/SANDBOX.md — real attempt_dir(root, name) and release(directory, root). release writes _released.txt and does not delete. name is one segment. Module selftest printed `sandbox selftest ok` (exit 0).
- library/resources/REQUIREMENTS.md — cold machine. `py -3.14 --version` printed `Python 3.14.0`. doctor exit 0 with vault_exists true while SPIDERCASTER_VAULT was unset. seat architect exit 0. crew selftest not run. No credentials.env.

Writer: SpiderCaster environment note for the attempt sandbox. Not a site build.

Scope:
- Wait, then read lib/sandbox.py if it is on disk.
- SANDBOX.md describes attempt_dir(root, name) and release(directory, root).
- REQUIREMENTS.md is the cold-machine list. py -3.14 --version only. No crew. No library bind --live.
- No credentials.env. No secret contents. No Cloudflare ids.

Started: 2026-10-01
