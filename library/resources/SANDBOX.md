# Attempt sandbox

Read from `lib/sandbox.py` on disk on 2026-10-01. This describes that module. It is not a stand-in contract. It does not build a site. `spidercaster.py` has no sandbox subcommand.

From `V:\a\Ai\spidercaster\working`, `py -3.14 lib\sandbox.py` printed `sandbox selftest ok` and exited 0. That selftest uses `tempfile.TemporaryDirectory`. `release` does not delete the attempt. The temporary root goes away only because the `with` block ends.

## attempt_dir(root, name) -> Path

Creates `root/name` and returns the resolved directory. `name` must be one path segment. The result must stay inside `root`.

`root` must already be a directory (`Path.is_dir`). Otherwise `ValueError`: `root must be an existing directory`.

`name` raises `ValueError` `attempt name must be one path segment` when any of these is true:

- it is not a `str`, or it is empty
- it is `.` or `..`
- it contains `/` or `\`
- `Path(name)` is absolute, has a drive, has an anchor, or `path.name != name`

The directory is `(root.resolve() / name).resolve()`. `mkdir(exist_ok=True)` creates it or reuses it. A second call with the same name does not wipe the directory. If `root/name` already exists and is not a directory, `mkdir` raises `FileExistsError`.

After resolve, the path is refused with `ValueError` `attempt directory is outside root` when it is not strictly inside the resolved root. The root itself does not count as inside. The same error is raised if the final path is not a directory. The return value is that resolved directory.

## release(directory, root) -> None

Writes `_released.txt` inside `directory`. Does not delete the directory or anything under it.

`root` must already be a directory, with the same error text as above. `directory` must resolve to a directory strictly inside that root. If it is missing, not a directory, equal to the root, or outside the root, `ValueError` is `directory is outside root`.

The marker path is `resolved / "_released.txt"`. If that path is a symlink, or it is not inside the root, the same outside-root error is raised and nothing is written. Otherwise the file is written as UTF-8 text `released` with no added newline. A later `release` overwrites that file. The attempt directory is still on disk after the write.

## What the module selftest checks

Under a temporary root it calls `attempt_dir(root, "job1")` and expects that directory. It rejects `..`, `a/b`, and an absolute path string. It then calls `release` and asserts the directory still exists and `_released.txt` reads `released`.
