STARTED

Adding read-only MCP tools for library callables: skill_read, hook_match, perm_rule, tool_search_local, seat_tools, seat_gate, layer_read, code_refuse, mold_panel. session_mark stays a library function. No live bind. No web search. No stock URL. No publish. No secrets.

Started: 2026-10-01

DONE

Registered nine read-only tools in mcp_server.py TOOLS and TOOL_SPECS: skill_read, hook_match, perm_rule, tool_search_local, seat_tools, seat_gate, layer_read, code_refuse, mold_panel. Each calls the library function and returns its dict. Import failure returns isError. skill_read returns isError missing because lib.skill_read is not on disk. layer_read refuses a write argument. mold_panel refuses a live argument and reads the package root. session_mark was not added. No live bind. No web search. No stock URL. No publish. No secrets. Existing tools were not changed.

Self-check: mcp wave2 ok

Done: 2026-10-01
