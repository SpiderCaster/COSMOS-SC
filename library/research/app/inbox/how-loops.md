STARTED 2026-10-01

Research how professional agent systems use loops and triggers to raise output quality. Public docs only. Open Claude Code hooks, a CI retry or visual-check loop (GitHub Actions or a documented critique loop), and one site-builder QA loop if a public page exists (Wix, Framer, or Relume). Cite URLs. If a step is not public, write not public. Read lib/crew.py run_job. End HOW_LOOPS.md with a trigger table of at most 6 rows: event, condition, action, max times. Actions may only be rerender once, fail closed, or record. No action may publish or call an image API. No Python edits. No publish. No secrets.

DONE 2026-10-01

Wrote library/research/app/HOW_LOOPS.md. Opened Claude Code hooks and the hooks guide, GitHub's re-run page (30 days, 50 re-runs, same SHA) and workflow fail-fast (matrix default true), Wix Get Feedback, Framer preview, and Relume's sitemap generation pause. run_job runs seven seats once, breaks on the first FAIL, still appends deployer, and does not render again or publish. The note ends with six trigger rows. Actions are only rerender once, fail closed, or record. No Python edits. No publish. No secrets.
