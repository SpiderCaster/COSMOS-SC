DONE 2026-10-01 14:41:12

check_site reads every file in <project>/copy whose suffix is .md, .markdown, or .txt, in sorted name order, and concatenates that text with newlines. After Start-Sleep 90, lib.check.check_site accepts copy_text, so the hand calls check_mod.check_site(dest, expect_noindex=True, quiet=True, copy_text=copy_text). quiet=True stays from the existing call. HANDS keys are unchanged. Local hero behavior is unchanged. Selftest was not extended and does not require an ungrounded_claim failure.

py -3.14 -m lib.hands.selftest
hands selftest ok
