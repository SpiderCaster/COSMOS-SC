# Wallet map - Google AI draw sources (recorded 2026-09-28)

Metadata only: key files referenced by path, identified by last4 + short
SHA-256 fingerprint. **No key values in this file, ever.** Values live in
`V:\Research4\.secrets\` (or the OpenWork/OpenCode occupant stores).

Measured 2026-09-28 via Vertex express probes + bogus-model project
discovery (the 404/403 message names the owning project).

## The three 2026-09-20 trial wallets (FIFO candidates)

| wallet | key file (V:\Research4\.secrets\) | last4 | fp | project number | status measured 9/28 |
|---|---|---|---|---|---|
| MedicineMan | `vertex_medicineman_key.txt` | `BZIg` | `50748b` | **456875530590** | Vertex express LIVE. **Expires ~Oct 8-14 2026** (registered ~Jul 10-14 + 90 days; Keith, from trial emails 2026-09-28 — approximate; supersedes an earlier Dec reading). |
| Fruitaholics | `vertex_fruitaholics_key.txt` | `B9Rg` | `b1b221` | **953760228233** | Vertex express LIVE. **Expires ~Oct 8-14 2026** (same basis — approximate). |
| PatriotFuelStop | `vertex_patriotfuelstop_key.txt` | `2qDQ` | `5986e9` | **571047330544** | Vertex express LIVE. **Expires ~Oct 8-14 2026** (same basis — approximate). |

- Registration/expiry dates NOT recorded anywhere locally; read per account
  in console > Billing > Credits. If July-registered: 90-day cliff lands
  early-to-mid Oct 2026 (days away). If 9/20-registered: ~Dec 19, 2026.
- MECHANISM (Keith, 2026-09-28): expiry = registration + 90 days, period.
  Converting to a billing account (Activate) preserves the remaining dollars
  but does NOT extend the window - Joanna precedent: registered Jul 14,
  activated Sep 4, window still ended Oct 13 (= Jul 14 + 90). Never plan
  around activation buying time.
- AI Studio (generativelanguage) is NOT enabled on these three; Vertex
  express (Agent Platform) IS. The engine reaches them via the vertex route.

## Older wallets (from the COSMOS index + .secrets)

| wallet | key source | last4 | fp | project | status |
|---|---|---|---|---|---|
| openwork-csm | env `GEMINI_API_KEY`/`GOOGLE_API_KEY` AND `~/.opencode/auth.json` google (same key, fp match) | `D6rQ` | `704bb5` | **252939746739** | BLOCKED: Agent Platform API never enabled on the project (403). OpenWork + OpenCode draw this one wallet today. |
| Joanna (Keith's OpenWork target) **<-- ACTIVE DRAW** | `vertex_key.txt` | `3fMQ` | `141811` | `project-5a33f910-1251-4d6a-bf9` | **$142.36 remaining** (Keith, read from Credits page 2026-09-28 — MEASURED, not computed). Discount eligibility offered after credits exhaust. Window ends **2026-10-10** (Keith, read from the console — supersedes the computed Oct 13). Vertex express LIVE (re-probed 9/28). |
| Kelly / orders.ggn (COSMOS + Crucible) | `vertex_coding_key.txt` | `Ko_A` | `0bc221` | `project-10b3a132-ec5b-41e9-a2c` | $300 through **2026-12-04** |
| keith.bbf AI Studio "My First Project" | `gemini_key.txt` | `jvmA` | `213147` | **475026348209** | Free tier, rate-capped (RPD 20-22/20; ~300x 429 in Jul) |
| keith.bbf depleted key | `gemini_key.txt.depleted-2026-08-12.bak` | `rgXw` | `2a00b3` | - | depleted 2026-08-12 |
| keith.bbf "Default Gemini Project" | index only (key `openw-cos`, not in .secrets) | `cLGw` | - | `gen-lang-client-0129519884` | per COSMOS index |
| Ranny AI Studio (Jack's) | index only (`openw-cosmos`, not in .secrets) | `9gXw` | - | `gen-lang-client-0877976774` | Jack's OpenWork only |
| Ranny Cook GCP (Jack's) | OAuth client in `~/.opencode/auth.json` (no API key file) | - | - | `project-5c0bf0ae-c45a-4d2c-bab` / 249427005764 | Jack's $300, hands off |

## FIFO draw order (earliest expiry first; expiry = registration + 90, activation never extends it)

**ACTIVE DRAW (Keith, 2026-09-28): Joanna — $142.36 measured, window ends Oct 10
(Keith, read from the console; the earlier Oct 13 was computed, not read).**
User-level env `FORGE_GEMINI_KEY_FILE` points at `vertex_key.txt`, so every
engine run draws Joanna by default. The ledger records `draw: vertex_key.txt`
per call. To burn a different wallet, override the env var for that run.

1. **The October cluster — ALL FOUR wallets die Oct 8-14.** Joanna ($142.36,
   Oct 10) + MedicineMan / Fruitaholics / PatriotFuelStop ($300 each,
   ~Oct 8-14). ~$1,042 total, ~2 weeks to burn. Plan: stay on Joanna (default
   draw) through Oct 10, then rotate medicineman -> fruitaholics ->
   patriotfuelstop daily until they die. Unspendable by hand at ~3k
   tokens/build — the risk is forgetting to switch, not running out.
2. **Kelly — the only December wallet.** $300 through 2026-12-04; the stable
   rail after the cluster dies. Becomes the default draw on ~Oct 14.

Ranny (both) is Jack's - never draw it from Keith's seats.

## Engine hook

```powershell
$env:FORGE_GEMINI_KEY_FILE = 'V:\Research4\.secrets\vertex_medicineman_key.txt'
python forge.py wallets     # fingerprint map; marks the active draw
python forge.py build projects/<name> --out sites/<name>
```

Fail-closed: if the key file is set but unreadable, the engine refuses rather
than silently drawing another wallet.
