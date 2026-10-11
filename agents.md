# AGENTS.md — SpiderCaster lane rules (read before tracing, writing, or refactoring)

1. **No file-hopping (why: context rot).** You are contained in your lane (engine/seats/parts/tools).
   Sessions + cosmos_core are COSMOS-side black boxes — never read, never import.
2. **Zero cross-imports (why: hallucination containment).** Lanes talk via JSON contracts
   (tickets, seat packs, ledger rows, manifests) over engine entry points — never `import` across lanes.
3. **Localized tests (why: blast radius).** Every lane carries `*_selftest.py` beside its code;
   prove lane-green before claiming done. Fix local bugs locally; never propose global rewrites.
4. **Gates over sentences (why: models invent).** No lane is done until `check` + `shipcheck` + 6Cs pass;
   a model sentence is never the gate. Unrun = NOT RUN, never PASS.
