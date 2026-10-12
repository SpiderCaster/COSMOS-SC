#!/usr/bin/env python3
"""secret_scan.py - block commits that contain secrets.

Usage:
    python scripts/secret_scan.py            # scan staged files (pre-commit mode)
    python scripts/secret_scan.py --all      # scan tracked + untracked, non-ignored files
    python scripts/secret_scan.py PATH ...   # scan specific files

Prints only  file:line  <pattern name>.  It NEVER prints the matched value.
Exit code 1 when something is found, 0 when clean.

Suppress a reviewed false positive with  secret-scan: ignore  in a comment on that line.

Optional local check: if the env var SC_KNOWN_SECRET_FILES (os.pathsep-separated)
or the default local key files exist, any literal value (8+ chars) from them that
appears in a scanned file is reported as  known-value:<NAME>  (name only).
"""
import os
import re
import subprocess
import sys

MAX_BYTES = 2_000_000

# Reviewed files whose matches are deliberate fake fixtures (path suffixes).
ALLOW_PATHS = ("tools/sidebars-widgets/selftest.py",)

FORBIDDEN_NAMES = [
    (re.compile(r"(^|/)\.env($|\.(?!example$|sample$|template$))", re.I), "env-file"),
    (re.compile(r"(^|/)credentials\.env$", re.I), "credentials-file"),
    (re.compile(r"\.(pem|key|pfx|p12|jks|kdbx)$", re.I), "key-file"),
    (re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)(\.|$)", re.I), "ssh-private-key-file"),
    (re.compile(r"(^|/)keys/", re.I), "keys-directory"),
]

PATTERNS = [
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY( BLOCK)?-----")),
    ("openai-style-key", re.compile(r"\bsk-(?:proj-|ant-|or-v1-)?[A-Za-z0-9_\-]{20,}")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("stripe-key", re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("bearer-token-literal", re.compile(r"(?i)\bBearer\s+(?!<|\{|\$|%|token\b|your|xxx|\*)[A-Za-z0-9_\-\.=]{24,}")),
    ("url-with-credentials", re.compile(r"(?i)\b[a-z][a-z0-9+.\-]*://[^/\s:@\"']+:[^/\s:@\"']{3,}@[^/\s\"']+")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
]

ASSIGN = re.compile(
    r"(?i)\b[A-Za-z0-9_.\-]*(?:password|passwd|pwd|secret|token|api[_\-]?key|apikey|license[_\-]?key|"
    r"access[_\-]?key|private[_\-]?key|auth[_\-]?key)[A-Za-z0-9_.\-]*[\"']?\s*[:=]\s*[\"']?"
    r"([A-Za-z0-9_\-+/=.!@#%^&*]{12,})"
)
PLACEHOLDER = re.compile(
    r"(?i)(\*{3,}|x{4,}|your|example|changeme|placeholder|redacted|dummy|sample|<|>|\$\{|\$\(|%[A-Za-z_]+%|"
    r"^\.{2,}|fill.?manually|todo|none|null|true|false|environ|getenv)"
)


SECRETISH = re.compile(r"(?i)(password|passwd|pass$|secret|token|api_?key|license|access_?key|private)")


def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout


def git_files(mode):
    if mode == "staged":
        out = run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"])
    else:
        out = run(["git", "ls-files", "-co", "--exclude-standard", "-z"])
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def read_blob(path, staged):
    if staged:
        return run(["git", "show", ":" + path])
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return b""


def load_known_values():
    files = [p for p in os.environ.get("SC_KNOWN_SECRET_FILES", "").split(os.pathsep) if p]
    files += [r"V:\streams\webdev\keys\.env", r"V:\streams\webdev\spidercaster_local\credentials.env"]
    known = {}
    for fp in files:
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*(.*?)\s*$", line)
                    if not m:
                        continue
                    name, val = m.group(1), m.group(2).strip().strip("\"'")
                    if (len(val) < 12 or not SECRETISH.search(name) or PLACEHOLDER.search(val)
                            or val.startswith("$")):
                        continue
                    known.setdefault(val, name)
        except OSError:
            continue
    return known


def scan_text(path, text, known):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if "secret-scan: ignore" in line:
            continue
        if len(line) > 5000:
            line = line[:5000]
        for name, rx in PATTERNS:
            if rx.search(line):
                hits.append((n, name))
        for m in ASSIGN.finditer(line):
            v = m.group(1)
            if PLACEHOLDER.search(v):
                continue
            if re.search(r"[A-Za-z]", v) and re.search(r"\d", v) and not re.fullmatch(r"[A-Za-z_.]+\(?", v):
                hits.append((n, "secret-assignment"))
                break
        for val, nm in known.items():
            if val in line:
                hits.append((n, "known-value:" + nm))
    return hits


def main(argv):
    args = argv[1:]
    if args and args[0] == "--all":
        paths, staged = git_files("all"), False
    elif args:
        paths, staged = args, False
    else:
        paths, staged = git_files("staged"), True
    known = load_known_values()
    found = 0
    for p in paths:
        norm = p.replace("\\", "/")
        if norm in ALLOW_PATHS:
            continue
        for rx, name in FORBIDDEN_NAMES:
            if rx.search(norm):
                print("%s:0  forbidden-filename:%s" % (norm, name))
                found += 1
                break
        data = read_blob(p, staged)
        if not data or len(data) > MAX_BYTES or b"\0" in data[:8192]:
            continue
        for n, name in scan_text(norm, data.decode("utf-8", "replace"), known):
            print("%s:%d  %s" % (norm, n, name))
            found += 1
    if found:
        sys.stderr.write("secret_scan: %d finding(s). Values are not printed. Fix, or mark reviewed "
                         "false positives with 'secret-scan: ignore'.\n" % found)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))