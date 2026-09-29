#!/usr/bin/env python3
"""Seat an Antigravity SDK agent on the SpiderCaster engine.

Wires the spidercaster MCP server (mcp_server.py, stdio) into an Antigravity
SDK Agent with role-based tool policies matching mcp/HARNESS_CONFIGS.md:

  planner   catalog_read, tokens_read, brand_read, pagemodel_read, draft_offline
  builder   planner tools + pagemodel_write(full) + render_trigger + validate_run
  content   brand_read, pagemodel_read, pagemodel_write (patch role), render_trigger
  reviewer  catalog_read, pagemodel_read, render_trigger, validate_run, review_write

The engine enforces write rules server-side (role param); these policies are
defense in depth - the agent never even sees tools outside its role.

Requires: pip install google-antigravity  (compiled runtime from PyPI; the
git clone alone is NOT sufficient). The agent draws whatever wallet
FORGE_GEMINI_KEY_FILE points at - the env var is merged into the MCP
subprocess, and the SDK agent itself uses the SDK's own auth.

Usage:
  python antigravity_seat.py --role builder
  python antigravity_seat.py --role reviewer
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MCP_SERVER = ROOT / "mcp_server.py"

ROLE_TOOLS = {
    "planner": ["catalog_read", "tokens_read", "brand_read", "pagemodel_read", "draft_offline"],
    "builder": ["catalog_read", "tokens_read", "brand_read", "pagemodel_read",
                "pagemodel_write", "render_trigger", "validate_run"],
    "content": ["brand_read", "pagemodel_read", "pagemodel_write", "render_trigger"],
    "reviewer": ["catalog_read", "pagemodel_read", "render_trigger", "validate_run", "review_write"],
}

ROLE_PROMPT = {
    "planner": "You are the SpiderCaster planner. Read the brand and copy, propose site structure. Read-only.",
    "builder": "You are the SpiderCaster builder. Assemble site models from real copy; never invent facts; noindex by default.",
    "content": "You are the SpiderCaster content seat. Patch text in existing sections only; never change structure; never invent facts.",
    "reviewer": "You are the SpiderCaster reviewer. Validate rendered sites with counts, never adjectives; write review results.",
}


async def main() -> int:
    ap = argparse.ArgumentParser(prog="antigravity_seat")
    ap.add_argument("--role", choices=sorted(ROLE_TOOLS), default="builder")
    ap.add_argument("--surface-root", default=os.environ.get("SPIDERCASTER_SURFACE_ROOT") or str(ROOT / "sites"))
    args = ap.parse_args()

    try:
        from google.antigravity import Agent, LocalAgentConfig
        from google.antigravity.types import McpStdioServer
        from google.antigravity.hooks import policy
        from google.antigravity.utils.interactive import run_interactive_loop
    except ImportError:
        print("google-antigravity is not installed. Run:  pip install google-antigravity")
        print("(the compiled runtime ships in the PyPI wheels; the git clone alone is not enough)")
        return 1

    server = McpStdioServer(
        name="spidercaster",
        command=sys.executable,
        args=[str(MCP_SERVER)],
        env={"SPIDERCASTER_SURFACE_ROOT": args.surface_root},
    )
    tools = ROLE_TOOLS[args.role]
    policies = [
        policy.deny_all(),
        policy.allow(server, tools),
    ]
    config = LocalAgentConfig(
        system_instructions=ROLE_PROMPT[args.role],
        mcp_servers=[server],
        policies=policies,
    )
    print(f"SpiderCaster seat: role={args.role}")
    print(f"  tools: {', '.join(tools)}")
    print(f"  surface root: {args.surface_root}")
    await run_interactive_loop(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
