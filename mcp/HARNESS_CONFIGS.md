# Siteforge MCP - harness configs

One server, every harness. The engine stays here; agents keep their own
harnesses (no re-homing). Each config below points at the same stdio server.
Windows paths use forward slashes (Python accepts them natively).

Server: `V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py`
Surface root (optional env): `SITEFORGE_SURFACE_ROOT` (default: `siteforge/sites`)
Secrets dir (optional env): `SITEFORGE_SECRETS_DIR` (default: `V:\Research4\.secrets`)

## Claude Code

```
claude mcp add siteforge -- python V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py
```

or `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "siteforge": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py"],
      "env": { "SITEFORGE_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/siteforge/sites" }
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
name = "siteforge"
command = "python"
args = ["V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py"]
env = { SITEFORGE_SURFACE_ROOT = "V:/Streams/WEBSITES/openwork_space/siteforge/sites" }
```

Approval policy: the engine tools are local, trusted operations on Keith's own
surface - safe to auto-approve. Keep `pagemodel_write` role-restricted in the
agent prompt (builder vs content), not just in config.

## Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "siteforge": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py"],
      "env": { "SITEFORGE_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/siteforge/sites" }
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
    "siteforge": {
      "command": "python",
      "args": ["V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py"],
      "env": { "SITEFORGE_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/siteforge/sites" }
    }
  }
}
```

Ask mode is default: add the siteforge tools to the allowlist so they run
without per-call approval (local, trusted).

## OpenCode

Project `opencode.json`:

```json
{
  "mcp": {
    "siteforge": {
      "type": "local",
      "command": ["python", "V:/Streams/WEBSITES/openwork_space/siteforge/mcp_server.py"],
      "environment": { "SITEFORGE_SURFACE_ROOT": "V:/Streams/WEBSITES/openwork_space/siteforge/sites" }
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

## Later (when the capability is needed)

- `chrome-devtools-mcp` OR `@playwright/mcp` - reviewer inspects rendered
  output in a real browser (pick one)
- GitHub MCP - once the engine repo lands on github.com/SpiderCaster (account
  created 2026-09-28, 0 repos so far - nothing to connect yet)
- Not needed for MVP: database/analytics/payments MCPs
