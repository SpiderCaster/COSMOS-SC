# tool-sandbox

STATUS: DONE

Attempt sandbox is `lib/sandbox.py`. `attempt_dir` creates one path segment inside an existing root and refuses `..`, a slash, a backslash, and an absolute name. `release` writes `_released.txt` with the single word released and does not delete the attempt.

Selftest (`py -3.14 -m lib.sandbox`):

```
sandbox selftest ok
```

Done: 2026-10-01 14:41:10
