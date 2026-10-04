# Loops and triggers that raise output quality

Read 2026-10-01. Public rules are paraphrased next to the page that states them. A number appears here only when that page states it. This note does not change `lib/crew.py`. It does not publish. It does not call an image API.

Scope: how a professional system decides to try again, stop, or only record, and what a six-row cap would mean for SpiderCaster. The trigger table at the end is a bound, not a claim that the code already loops.

## What SpiderCaster does today

`lib/crew.py` `run_job` runs seven seats. Package order is architect, content, frontend, graphics, visual, seo, deployer. A saved workflow may reorder the first six. Deployer is forced last.

The work loop does not enter deployer. Each other seat runs its hands once, in list order. Architect: `brief_read`, `frame_pick`, `mold_pick`, `library_bind`. Content: `copy_read`, `copy_gap`. Frontend: `plan_offline`, `render`. Graphics: `asset_list`, `vault_photos`. Visual: `check_site`. SEO: `uniqueness`, `meta_basics`.

`library_bind` can FAIL before the hand runs, when the mold id is already live on another site. Any hand whose status is `FAIL` sets `stopped` and breaks that seat's remaining hands. The loop then breaks, so later work seats do not run and are not written as rows. A seat that is all `SKIP` is `SKIP`. A seat with no `FAIL` is `PASS`. `SKIP` does not stop the job.

Deployer is appended after that loop, not inside it. Its status is `FAIL` if any earlier row is `FAIL`, otherwise `PASS`. The detail string is the ticket note. `ticket_write` still runs. The docstring says the function writes the site and `crew-ticket.json` and does not publish. `ctx["live"]` is `False`. No seat runs twice. Nothing in `run_job` calls `render` again after a `FAIL`.

## Claude Code hooks

Hooks are user-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents that run at points in the session. The point of a command hook is deterministic control: the action happens because the event fired, not because the model chose to run it. Judgment hooks exist too: a prompt hook is one model call, and an agent hook is a subagent. The guide says to prefer command hooks for production. The agent type is experimental. https://code.claude.com/docs/en/hooks-guide

Cadence on the reference page: per session (`SessionStart`, `SessionEnd`), per turn (`UserPromptSubmit`, `Stop`, `StopFailure`), and on every tool call inside the agentic loop (`PreToolUse`, `PostToolUse`), except `EndConversation`, which skips both. https://code.claude.com/docs/en/hooks

A matcher picks the event. An optional `if` can skip the process spawn. Exit 0 with no output is silence, not approval. Exit 2 is the blocking code. On `PreToolUse` it blocks the tool call. On `Stop` it prevents Claude from stopping and continues the conversation. On `TaskCompleted` it prevents the task from being marked completed. Exit 1, without valid decision JSON, is a non-blocking error: the action proceeds. A command, HTTP, or MCP hook that hits its timeout does not block `PreToolUse`. The reference says not to count on a stalled hook as a gate. https://code.claude.com/docs/en/hooks

`Stop` is the quality loop. A prompt hook returns `ok`. `ok: false` feeds `reason` back as the next instruction and the turn continues, unless the model also sets `impossible: true`, in which case the turn is allowed to end. `stop_hook_active` is true when a stop hook is already continuing the turn. The same page states an 8-consecutive-continuation cap: after stop hooks have continued eight times in a row, the next block is overridden and the turn ends. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` can raise that cap. `/goal` is a built-in shortcut for a session-scoped prompt Stop hook. An agent hook may use tools such as Read, Grep, and Glob, and after up to 50 turns returns `ok`. The reference says to prefer command hooks in production. https://code.claude.com/docs/en/hooks

`FileChanged` is the infinite-rewrite warning. The sample normalizes line endings and greps for a carriage return first, so the run after a real change exits without touching the file. The page says a looser guard loops forever, because a rewrite fires the hook again. `once: true` on a skill hook removes that hook after its first successful run. https://code.claude.com/docs/en/hooks

`PermissionDenied` can return `retry: true` so the model may retry the denied tool call. The reference says Claude Code ignores `retry` when the classifier produced no verdict. That retry is not a counted quality loop on the page. A numeric cap for it is **not public** there. https://code.claude.com/docs/en/hooks

What this is for SpiderCaster: the checker should be a command, not a hope that a seat will look again. A fail that cannot be fixed by another local render should end the job (`impossible`), not continue. A fail that might be a bad render gets one more render, then the same flag the Stop hook uses (`stop_hook_active`) so the second fail cannot start a third. Eight continuations and a 50-turn verifier are public Claude Code caps. They are too loose for one static page, and they are not adopted below.

## GitHub Actions

Re-running workflows and jobs is a human retry, not an automatic one. Someone with write permission on the repository can re-run the whole workflow, only the failed jobs, or one job, up to 30 days after the initial run. The re-run uses the privileges of the actor who first triggered the workflow, and the same `GITHUB_SHA` and `GITHUB_REF` as the original event. A workflow run can be re-run a maximum of 50 times. That limit counts full re-runs and re-runs of a subset of jobs. The run page keeps earlier attempts: the Latest menu can open a previous attempt. https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs

An automatic retry count inside a job step is **not public** on that page.

The workflow syntax page is the stop, not the retry. `jobs.<job_id>.strategy.fail-fast` applies to the whole matrix. If it is `true`, GitHub cancels in-progress and queued jobs in the matrix when any job in the matrix fails. The property defaults to `true`. `continue-on-error: true` on one job lets the other matrix jobs keep going when that job fails. https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

On the same page, hosted runners enforce fail-fast in the shell: bash and sh use `set -e` by default, and bash also uses `-o pipefail`. PowerShell prepends `$ErrorActionPreference = 'stop'`. Those are step failures, not a second render. https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

What this is for SpiderCaster: `run_job` already matches matrix `fail-fast`. The first `FAIL` cancels the seats that have not started. It does not match "re-run failed jobs," because nothing runs again, and the skipped seats are missing from the ticket rather than recorded. A quality retry, if one is added, should be one local render of the page that just failed the checker, on the same inputs, and then stop. Fifty is the public GitHub cap for a human re-running a workflow. It is not the cap in the table below. Previous attempts should be recorded. GitHub keeps them. SpiderCaster today keeps one ticket.

## Site-builder QA

### Wix

Wix Editor Get Feedback is a critique loop on the saved site before publish. Every site has a link. Recipients see the most recently saved version and can leave comments. They open the link, click Add Comments, and drag a comment onto an area. The owner gets an Editor alert and an email, can jump to the spot, reply, or resolve, and can filter open versus resolved. Desktop and mobile comments are separate views inside the app. Comments cannot be added from a mobile browser. The shareable link is valid for 2 weeks. Anyone with the link can view password-protected pages and Members Only pages. https://support.wix.com/en/article/wix-editor-getting-site-feedback

A rule that unresolved comments block publish is **not public** on that page. A max comment count, an automatic re-render, and an image-generation step are **not public** there.

### Framer

Framer preview is a look-before-publish loop, not a scored gate. Preview mode shows the site as visitors will see it so you can check layout, responsiveness, and interactions before publishing. Open it with the Play button, or Command-P on macOS, or Ctrl-P on Windows. In preview, resize the viewport, or open a selected breakpoint such as Tablet. Exit with the button or Esc. Custom code added through Settings does not appear in the preview. That code is only visible on the published site. https://www.framer.com/help/articles/how-to-preview-your-site/

A pass/fail score, a retry count, and a control that blocks the publish button are **not public** on that page. The page also says a preview cannot stand in for the published result when the thing under test is Settings custom code.

### Relume

Relume Site Builder generates the Home page first and waits. The doc says that pause is the chance to see if the direction is right before pressing "continue generating pages." Sitemap edits (page names, section names, section descriptions, added sections) should happen before wireframes, because that step influences what the wireframes become. A second sitemap is another generation: the plus icon under the primary sitemap, then compare, and move the better one to the top to make it primary. The doc says to do this to test a prompt change. https://www.relume.ai/resources/docs/building-a-sitemap-with-ai

A numeric cap on how many sitemaps you may generate is **not public** on that page. A publish block is **not public** there. Color on a sitemap section does not change the wireframe. It is only a visual mark.

## What the three systems share

The gate is outside the generator. Claude Code runs a hook whether or not the model asks. GitHub fails the job on a non-zero exit and, for a matrix, cancels the rest by default. Wix collects critiques on a saved copy before publish. Framer makes preview a different step from publish, and says Settings custom code is absent from that preview. Relume shows Home before it spends the rest of the generation, and can keep a second sitemap beside the first.

The dangerous pattern is also public. A FileChanged hook that rewrites the file every time never stops. A Stop hook that keeps saying "not done" is cut off at eight unless an operator raises the cap. GitHub will re-run the same SHA up to 50 times, but a person chooses each re-run, and failed-only re-runs do not repeat the green jobs.

SpiderCaster has the stop and not the retry. The first `FAIL` drops the remaining work seats. The ticket still records the failing seat and a deployer `FAIL`. It does not record the seats that never started. It does not render again.

## Trigger table

These rows are the only retries and stops this note allows. Action is one of: rerender once, fail closed, record. "Rerender once" means the local frontend `render` hand only, on the same project, mold, and copy. It does not publish. It does not call an image API. It does not run graphics, vault, or imagine. A second firing of the same check does not match the rerender row.

| event | condition | action | max times |
| --- | --- | --- | --- |
| hand FAIL before a page exists | `FAIL` on brief, frame, mold, `library_bind`, copy, plan, asset list, or vault photos, including a mold id already live on another site | fail closed | 1 |
| `check_site` FAIL | frontend `render` has already run once in this job, and this job has not rerendered | rerender once | 1 |
| `check_site` or `meta_basics` FAIL | the one rerender already ran, or the check failed again | fail closed | 1 |
| `uniqueness` FAIL | mold id is already live on another site | fail closed | 1 |
| seat ends, or a later seat never starts | status is `PASS`, `SKIP`, or `FAIL`, or the loop stopped before that seat | record | 1 |
| deployer | any recorded `FAIL`, including a `FAIL` after the one rerender | fail closed | 1 |

`SKIP` stays a record, not a stop, which is what `run_job` does now. Deployer fail closed writes the ticket and does not publish. No row is allowed to run twice. No row is allowed to call an image API.
