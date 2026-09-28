# SpiderCaster MCP - harness configs

One server, every harness. The engine stays here; agents keep their own
harnesses (no re-homing). Each config below points at the same stdio server.
Windows paths use forward slashes (Python accepts them natively).

Server: `V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py`
Surface root (optional env): `SPIDERCASTER_SURFACE_ROOT` (default: `SpiderCaster/sites`)
Secrets dir (optional env): `SPIDERCASTER_SECRETS_DIR` (default: `V:\Research4\.secrets`)

## Claude Code

```
claude mcp add spidercaster -- python V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py
```

or `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "spidercaster": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py"],
      "env": { "SPIDERCASTER_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/SpiderCaster/sites" }
    }
  }
}
```

Optional enrichment: a PostToolUse hook on `pagemodel_write` can append every
change to the ledger; hooks can also gate `render_trigger` completions.

## Codex CLI

`~/.codex/config.toml` (or `.codex/config.toml` per project):

```toml
[[mcp_servers]]
name = "spidercaster"
command = "python"
args = ["V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py"]
env = { SPIDERCASTER_SURFACE_ROOT = "V:/Streams/WEBSITES/openwork_space/SpiderCaster/sites" }
```

Approval policy: the engine tools are local, trusted operations on Keith's own
surface - safe to auto-approve. Keep `pagemodel_write` role-restricted in the
agent prompt (builder vs content), not just in config.

## Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "spidercaster": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py"],
      "env": { "SPIDERCASTER_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/SpiderCaster/sites" }
    }
  }
}
```

Tool allowlist per agent role: Content sees `pagemodel_read` + `pagemodel_write`
(patch role) + `brand_read`; Reviewer sees `validate_run` + `review_write` +
`render_trigger`; Builder sees everything except `review_write`.

## Antigravity

Workspace `.agents/mcp_config.json` (or global `~/.gemini/config/mcp_config.json`):

```json
{
  "mcpServers": {
    "spidercaster": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py"],
      "env": { "SPIDERCASTER_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/SpiderCaster/sites" }
    }
  }
}
```

Ask mode is default: add the SpiderCaster tools to the allowlist so they run
without per-call approval (local, trusted).

## OpenCode

Project `opencode.json`:

```json
{
  "mcp": {
    "spidercaster": {
      "type": "local",
      "command": ["python", "V:/Streams/WEBSITES/openwork_space/SpiderCaster/mcp_server.py"],
      "environment": { "SPIDERCASTER_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/SpiderCaster/sites" }
    }
  }
}
```

## Per-role tool allowlist (enforce in each harness's agent config)

| role | tools |
|---|---|
| Architect / planner | `catalog_read`, `tokens_read`, `brand_read`, `pagemodel_read`, `draft_offline` |
| Builder | `catalog_read`, `tokens_read`, `brand_read`, `pagemodel_read`, `pagemodel_write` (role=builder), `render_trigger`, `validate_run` |
| Content | `brand_read`, `pagemodel_read`, `pagemodel_write` (role=content, patch only) |
| Reviewer | `catalog_read`, `pagemodel_read`, `render_trigger`, `validate_run`, `review_write` (no pagemodel_write) |
| Editor / co-pilot | `pagemodel_read`, `pagemodel_write` (role=editor, patch only), `render_trigger`, `brand_write` |
| Ops / Keith | `wallets`, everything above |

The server enforces the write rules itself (role param): content/editor cannot
change section types or add pages; only builder writes full models. Config
allowlists are defense in depth on top.

## GitHub MCP (repo: github.com/SpiderCaster/COSMOS-SC)

The engine repo is live. Wire the official GitHub MCP so agents can read
issues/PRs/files without pasting. Two routes:

**Remote (Streamable HTTP, official):**

```
claude mcp add --transport http github https://api.githubcopilot.com/mcp
codex mcp add github --url https://api.githubcopilot.com/mcp --bearer-token-env-var GITHUB_PAT
```

Cursor / Antigravity (JSON):

```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp",
      "headers": { "Authorization": "Bearer ${GITHUB_PAT}" }
    }
  }
}
```

`GITHUB_PAT` is set by Keith in the environment (name only, never pasted into
files or chat). Claude Code can also use its OAuth flow on first `/mcp` use —
no PAT handling at all. Scope the PAT to `repo` on the SpiderCaster account.

## Later (when the capability is needed)

- `chrome-devtools-mcp` OR `@playwright/mcp` - reviewer inspects rendered
  output in a real browser (pick one). Note: the kit's `browser_check.py`
  already does this for bench rounds via Playwright.
- Not needed for MVP: database/analytics/payments MCPs
