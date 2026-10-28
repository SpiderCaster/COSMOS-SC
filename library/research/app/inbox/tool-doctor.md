DONE 2026-10-01

Read-only app tools only. Not a site build. No live bind. No credentials. No crew run.

- `lib/doctor.py` `report()`
- `lib/seatpack.py` `pack()`
- CLI `doctor` and `seat`

From `V:\a\Ai\spidercaster\working`:

- `py -3.14 -m lib.doctor` exit 0: `doctor selftest ok`
- `py -3.14 -m lib.seatpack` exit 0: `seatpack selftest ok`
- `py -3.14 spidercaster.py doctor` exit 0, compact json `"ok":true`
- `py -3.14 spidercaster.py seat architect` exit 0, compact json for architect
