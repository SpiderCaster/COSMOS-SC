STARTED
2026-10-01
Task: change make_public.py so the public snapshot is copied to a temp tree, leak-checked there, and only then replaces cosmos-sc-public. A failed check must leave the existing public tree untouched and exit 2. Do not publish. Do not bind --live. Never delete the working tree.

DONE
2026-10-01
make_public.py copies into a temp tree, runs the leak check there, and replaces cosmos-sc-public only when the check is clean. A failed check exits 2 and does not touch the existing public tree. Ran py -3.14 make_public.py from <repo-root>. Exit 0. files copied: 220 | excluded: 417. staged: <local-path> leak check: CLEAN (no internal emails, wallet names, project numbers, or key material). Working tree still present. No publish. No --live.
