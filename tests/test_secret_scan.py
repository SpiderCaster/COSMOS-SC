"""Tests for scripts/secret_scan.py.  Run:  python -m unittest tests.test_secret_scan -v

Every fake credential is assembled at runtime from short pieces, so this file
holds no realistic-looking secret literal and passes its own scan.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "secret_scan.py"

_spec = importlib.util.spec_from_file_location("secret_scan", SCRIPT)
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)

# --- fake values, built at runtime ------------------------------------------
FAKE_OPENAI = "sk" + "-" + "Ab1" * 10
FAKE_GITHUB = "gh" + "p_" + "Zy9" * 12
FAKE_AWS = "AK" + "IA" + "QWERTY12" * 2
FAKE_SLACK = "xo" + "xb-" + "1234567890" + "-abcdefghij"
FAKE_GOOGLE = "AI" + "za" + "Sy" + "A1b2C3" * 5 + "QRS"
FAKE_PEM = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
FAKE_ASSIGN = "q7Zk" + "93" + "mNpL" + "4x8B"        # letters+digits, 14 chars
FAKE_URL = "https://" + "svcuser" + ":" + "hunter22x" + "@" + "db.example.test/path"
KNOWN_VALUE = "Kn0wn" + "Val" * 5 + "99"            # 20 chars

ALL_VALUES = [FAKE_OPENAI, FAKE_GITHUB, FAKE_AWS, FAKE_SLACK, FAKE_GOOGLE, FAKE_ASSIGN,
              "hunter22x", KNOWN_VALUE]


def scan(text, path="sample.txt", known=None):
    return ss.scan_text(path, text, known or {})


def rules(text, **kw):
    return {r for _, r in scan(text, **kw)}


class PatternTests(unittest.TestCase):
    def test_blocks_each_token_shape(self):
        cases = {
            "openai-style-key": "key = " + FAKE_OPENAI,
            "github-token": "x " + FAKE_GITHUB,
            "aws-access-key-id": "id " + FAKE_AWS,
            "slack-token": "t " + FAKE_SLACK,
            "google-api-key": "g " + FAKE_GOOGLE,
            "private-key-block": FAKE_PEM,
            "url-with-credentials": "dsn " + FAKE_URL,
        }
        for rule, line in cases.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, rules(line))

    def test_blocks_secret_assignment(self):
        self.assertIn("secret-assignment", rules("api_key = " + FAKE_ASSIGN))
        self.assertIn("secret-assignment", rules('{"token": "%s"}' % FAKE_ASSIGN))

    def test_reports_line_numbers(self):
        hits = scan("clean\nclean\napi_key = %s\n" % FAKE_ASSIGN)
        self.assertEqual([n for n, _ in hits], [3])

    def test_clean_text_passes(self):
        clean = "\n".join([
            "# SpiderCaster notes",
            "def f(x): return x + 1",
            "api_key = os.environ['GEMINI_API_KEY']",
            "token = ${CLOUDFLARE_API_TOKEN}",
            "password: <your password here>",
            "OPENROUTER_API_KEY=changeme-example",
            "Authorization: Bearer <token>",
            "see https://example.com/docs and user@example.com",
        ])
        self.assertEqual(scan(clean), [])

    def test_placeholders_are_not_flagged(self):
        for v in ("xxxxxxxxxxxxxxxx", "your_api_key_here1", "${SOME_NAME_HERE}", "REDACTED-value-12"):
            with self.subTest(v=v):
                self.assertEqual(scan("api_key = " + v), [])


class AllowlistTests(unittest.TestCase):
    def test_inline_ignore_marker(self):
        line = "api_key = %s  # secret-scan: ignore" % FAKE_ASSIGN
        self.assertEqual(scan(line), [])
        self.assertNotEqual(scan("api_key = " + FAKE_ASSIGN), [])

    def test_allow_paths_skipped_by_main(self):
        self.assertIn("tools/sidebars-widgets/selftest.py", ss.ALLOW_PATHS)
        with tempfile.TemporaryDirectory() as d:
            old = os.getcwd()
            os.chdir(d)
            try:
                p = Path("tools/sidebars-widgets")
                p.mkdir(parents=True)
                (p / "selftest.py").write_text("api_key = %s\n" % FAKE_OPENAI)
                out, err, rc = run_main(["secret_scan.py", "tools/sidebars-widgets/selftest.py"])
            finally:
                os.chdir(old)
        self.assertEqual(rc, 0, out)
        self.assertEqual(out, "")

    def test_example_env_names_allowed(self):
        hit = lambda n: any(rx.search(n) for rx, _ in ss.FORBIDDEN_NAMES)
        self.assertFalse(hit(".env.example"))
        self.assertFalse(hit("config/.env.sample"))
        self.assertTrue(hit(".env"))
        self.assertTrue(hit("a/b/.env.local"))


class KnownValueTests(unittest.TestCase):
    def test_known_value_reported_by_name_only(self):
        with tempfile.TemporaryDirectory() as d:
            kf = Path(d) / "fake_keys.env"
            kf.write_text("FAKE_SERVICE_TOKEN=%s\n" % KNOWN_VALUE)
            old = os.environ.get("SC_KNOWN_SECRET_FILES")
            os.environ["SC_KNOWN_SECRET_FILES"] = str(kf)
            try:
                known = ss.load_known_values()
            finally:
                if old is None:
                    del os.environ["SC_KNOWN_SECRET_FILES"]
                else:
                    os.environ["SC_KNOWN_SECRET_FILES"] = old
        self.assertEqual(known.get(KNOWN_VALUE), "FAKE_SERVICE_TOKEN")
        hits = scan("note: " + KNOWN_VALUE, known=known)
        self.assertEqual(hits, [(1, "known-value:FAKE_SERVICE_TOKEN")])


def run_main(argv, known=None):
    """Call ss.main in-process with isolated known-values; return (stdout, stderr, rc)."""
    out, err = io.StringIO(), io.StringIO()
    saved = ss.load_known_values
    ss.load_known_values = lambda: known or {}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = ss.main(argv)
    finally:
        ss.load_known_values = saved
    return out.getvalue(), err.getvalue(), rc


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, name, text):
        p = Path(self.tmp) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return str(p)

    def test_clean_file_exit_0(self):
        p = self.write("ok.py", "print('hello')\nx = os.environ.get('GEMINI_API_KEY')\n")
        out, err, rc = run_main(["secret_scan.py", p])
        self.assertEqual((rc, out, err), (0, "", ""))

    def test_bad_file_exit_1_and_output_has_no_value(self):
        body = "\n".join([
            "a = '%s'" % FAKE_OPENAI, "b = '%s'" % FAKE_GITHUB, "c = '%s'" % FAKE_AWS,
            "d = '%s'" % FAKE_SLACK, "e = '%s'" % FAKE_GOOGLE, "api_key = %s" % FAKE_ASSIGN,
            "dsn = '%s'" % FAKE_URL,
        ])
        p = self.write("bad.py", body)
        out, err, rc = run_main(["secret_scan.py", p])
        self.assertEqual(rc, 1)
        self.assertGreaterEqual(len(out.strip().splitlines()), 7)
        combined = out + err
        for v in ALL_VALUES:
            self.assertNotIn(v, combined)
            self.assertNotIn(v[:8], combined)
        self.assertIn("openai-style-key", out)

    def test_known_value_never_printed(self):
        p = self.write("leak.txt", "x " + KNOWN_VALUE + "\n")
        out, err, rc = run_main(["secret_scan.py", p], known={KNOWN_VALUE: "FAKE_SERVICE_TOKEN"})
        self.assertEqual(rc, 1)
        self.assertIn("known-value:FAKE_SERVICE_TOKEN", out)
        self.assertNotIn(KNOWN_VALUE, out + err)

    def test_forbidden_filenames(self):
        for name, rule in ((".env", "env-file"), ("credentials.env", "credentials-file"),
                           ("deploy.pem", "key-file"), ("id_rsa", "ssh-private-key-file"),
                           ("keys/a.txt", "keys-directory")):
            with self.subTest(name=name):
                p = self.write(name, "nothing secret inside\n")
                out, _, rc = run_main(["secret_scan.py", p])
                self.assertEqual(rc, 1)
                self.assertIn("forbidden-filename:" + rule, out)

    def test_binary_and_oversize_skipped(self):
        p = Path(self.tmp) / "blob.bin"
        p.write_bytes(b"\0\0\0" + FAKE_OPENAI.encode())
        out, _, rc = run_main(["secret_scan.py", str(p)])
        self.assertEqual(rc, 0)

    def test_process_exit_codes_via_subprocess(self):
        good = self.write("g.txt", "fine\n")
        bad = self.write("b.txt", "api_key = %s\n" % FAKE_ASSIGN)
        r0 = subprocess.run([sys.executable, str(SCRIPT), good], capture_output=True, text=True)
        r1 = subprocess.run([sys.executable, str(SCRIPT), bad], capture_output=True, text=True)
        self.assertEqual(r0.returncode, 0)
        self.assertEqual(r1.returncode, 1)
        self.assertNotIn(FAKE_ASSIGN, r1.stdout + r1.stderr)


@unittest.skipUnless(shutil.which("git"), "git not available")
class StagedModeTests(unittest.TestCase):
    def test_staged_mode_scans_index_not_worktree(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*a):
                subprocess.run(["git", *a], cwd=d, check=True, capture_output=True)
            git("init", "-q")
            Path(d, "clean.txt").write_text("fine\n")
            Path(d, "leaky.txt").write_text("api_key = %s\n" % FAKE_ASSIGN)
            git("add", "clean.txt", "leaky.txt")
            r = subprocess.run([sys.executable, str(SCRIPT)], cwd=d, capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("leaky.txt:1", r.stdout)
            self.assertNotIn("clean.txt", r.stdout)
            self.assertNotIn(FAKE_ASSIGN, r.stdout + r.stderr)
            # fix the staged blob; worktree edits after staging must not matter
            Path(d, "leaky.txt").write_text("api_key = os.environ['X']\n")
            git("add", "leaky.txt")
            Path(d, "leaky.txt").write_text("api_key = %s\n" % FAKE_ASSIGN)
            r = subprocess.run([sys.executable, str(SCRIPT)], cwd=d, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)


class HookFileTests(unittest.TestCase):
    def test_hook_runs_scanner_and_blocks_on_failure(self):
        hook = (ROOT / "scripts" / "hooks" / "pre-commit").read_text()
        self.assertIn("scripts/secret_scan.py", hook)
        self.assertIn("exit 1", hook)
        raw = (ROOT / "scripts" / "hooks" / "pre-commit").read_bytes()
        self.assertNotIn(b"\r\n", raw, "hook must stay LF so it runs under git bash")


if __name__ == "__main__":
    unittest.main()