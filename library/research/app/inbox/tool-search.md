# tool-search

STATUS: DONE

Offline `lib/tool_search_local.py` only. Not a site. No network. No publish. No MCP import. The function does not write files.

`tool_search_local(query, catalog)` returns `ok`, `error`, `hits`, `limited`. Casefold substring. A name hit outranks a description hit. At most five `{name, description}` hits. `limited` is true when more than five matched. Rows that are not dicts, or that lack a non-empty string `name`, or whose `description` is not a string, are skipped. Failures: `empty_query`, `bad_catalog`, `no_match` (`hits` `[]`, `limited` false).

From `V:\a\Ai\spidercaster\working`:

- `py -3.14 -m lib.tool_search_local` exit 0: `tool_search selftest ok`

The six-item catalog asserted `limited` and `len(hits)==5`, an empty query fails, and a name hit ranks before a description-only hit.

Started: 2026-10-01
Done: 2026-10-01
