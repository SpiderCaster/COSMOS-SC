# MCP and seat tool gap

Second read was after a two-minute wait. `working/mcp_server.py` `TOOLS`, `working/spidercaster.py` subparsers, `working/lib/crew.py` `ROLES`, and `working/library/resources/INDEX.md` did not gain `doctor`, `seat`, `env_doctor`, or `seat_pack`.

A seat may call only its `ROLES` hands. MCP names below are the seven-seat allowlist in `working/mcp/HARNESS_CONFIGS.md`. `mcp_server.py` does not enforce that list. `crew run` sets `live` false. Publish on every row is no.

| Tool | Lives | Seat | Publish? |
|---|---|---|---|
| catalog_read | MCP | architect | no |
| tokens_read | MCP | architect, frontend | no |
| pagemodel_read | MCP | content, frontend | no |
| pagemodel_write | MCP | content (role=content), frontend (role=builder) | no |
| render_trigger | MCP | frontend | no |
| validate_run | MCP | visual, seo | no |
| review_write | MCP | none | no |
| brand_read | MCP | architect, content, graphics | no |
| brand_write | MCP | none | no |
| draft_offline | MCP | architect | no |
| wallets | CLI, MCP | none | no |
| crew_roles | CLI `crew roles`, MCP | none | no |
| mold_list | MCP | architect, seo | no |
| frame_list | MCP | architect (MCP only) | no |
| frame_pick | MCP, hand | architect | no |
| brief_read | hand | architect | no |
| mold_pick | hand | architect | no |
| library_bind | hand | architect (draft only) | no |
| copy_read | hand | content | no |
| copy_gap | hand | content | no |
| plan_offline | hand | frontend | no |
| render | hand | frontend | no |
| asset_list | hand | graphics | no |
| vault_photos | hand | graphics | no |
| check_site | hand | visual | no |
| uniqueness | hand | seo | no |
| meta_basics | hand | seo | no |
| ticket_write | hand | deployer | no |
| init | CLI | none | no |
| build | CLI | none | no |
| refine | CLI | none | no |
| check | CLI | none | no |
| serve | CLI | none | no |
| models | CLI | none | no |
| sections | CLI | none | no |
| image | CLI | none | no |
| library index | CLI | none | no |
| library list | CLI | none | no |
| library mold | CLI | none | no |
| library bind | CLI | none | no |
| library accept | CLI | none | no |
| library selftest | CLI | none | no |
| crew run | CLI | none | no |
| crew selftest | CLI | none | no |

`image` stays off every seat. `library accept` and `library bind --live` stay off every seat. This note does not add a live-bind tool or a crawl tool.

## Gaps still real after the second read

1. No CLI verb `doctor`.
2. No CLI verb `seat`.
3. No MCP tool `env_doctor`. `inbox/tool-mcp.md` was still STARTED.
4. No MCP tool `seat_pack`.
5. Thirteen `ROLES` hands are not in `TOOLS`: `brief_read`, `mold_pick`, `library_bind`, `copy_read`, `copy_gap`, `plan_offline`, `render`, `asset_list`, `vault_photos`, `check_site`, `uniqueness`, `meta_basics`, `ticket_write`. Only `frame_pick` is both a hand and an MCP tool.
6. `review_write`, `brand_write`, `wallets`, and `crew_roles` are in `TOOLS` and on no seven-seat allowlist. The server lists every tool to every client.
7. `frame_list` is an architect row in `INDEX.md` and an MCP tool. It is not in `ROLES` and not in `HANDS`, so `crew run` never calls it. The function exists in `lib/hands/__init__.py` and is unregistered.
8. `antigravity_seat.py` still seats planner, builder, content, and reviewer. Its content list includes `render_trigger`. The seven-seat content list does not.
9. `library_bind` writes live when `ctx["live"]` is true. Only `crew run` forces false. CLI `library bind --live` is still the publish click. No seat may use it.

Gap count: 9.
