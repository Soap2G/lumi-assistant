---
name: analysis-review
description: Use when the user wants a multi-reviewer critique of an analysis ARTIFACT — a notebook, an analysis-note PDF or text, or an analysis repo — judged for physics correctness, plot validity, and unmet commitments, ending in a single PASS / ITERATE / ESCALATE verdict. Defines the panel protocol: who reviews (the `reviewer-physics`, `reviewer-critical`, `reviewer-constructive` agents and the `plot-validator` skill), the A/B/C finding classes, panel composition per artifact type, the 3/5/10 iteration caps, the fresh-reviewer rule, and how the `arbiter` adjudicates. Does NOT gate a completion claim for a long-running compute step (that is `verification-before-completion`, the completion-evidence gate); does NOT extract numbers from one paper (that is `read-publication`); does NOT itself run the figure checks (that is `plot-validator`). Disambiguator phrase: A/B/C review-panel protocol.
data_scope: both
experiment: all
---

## What this is

A standalone, multi-agent review panel you can run on **any** analysis
artifact — an outreach notebook, an analysis-note PDF, or an analysis repo
with a `COMMITMENTS.md`. It exists because a single "looks done" gate misses
the errors a panel catches (wrong units, missing normalisation, zero-dof
fits, published values smuggled in as measurements, downscoped-to-death
commitments). The panel returns one verdict: **PASS / ITERATE / ESCALATE**.

This skill is the *protocol*. The reviewing is done by disposable subagents
(`reviewer-physics`, `reviewer-critical`, `reviewer-constructive`), the
figure checks by the `plot-validator` skill, and the verdict by the
`arbiter` agent. As the orchestrator you load this skill, spawn those
agents via the task tool, collect their text findings, and hand them to the
arbiter. (Subagents cannot be launched as the top-level agent — a primary
must delegate to them.)

## Finding classes (canonical — every reviewer uses these)

- **A — blocking:** invalidates the result as stated. Examples: MeV/GeV mix
  with no conversion; MC weight missing `sumOfWeights` or `mcWeight`; a fit
  with `ndf <= 0` (e.g. `chi2/ndf = 0/0`); unphysical negative yields; an
  unblinded signal region where blinding was required; a *published* value
  substituted as a measured input and presented as measured.
- **B — must-fix:** a real problem short of invalidating — a missing
  standard systematic, a deferred treatment of a known effect, weak binning,
  an undocumented assumption. **A self-flagged limitation that is fixable in
  the current phase is a B, not acceptable documentation** (the
  "diagnosis without treatment" failure).
- **C — style:** presentation and clarity — axis labels, figure aesthetics,
  wording.

## Panel composition by artifact type

| Artifact | Panel |
|---|---|
| Single plot / figure | `plot-validator` → `reviewer-physics` → `arbiter` |
| Notebook | `plot-validator` (on its figures) + `reviewer-physics` + `reviewer-critical` → `arbiter` |
| Analysis-note PDF / repo (+ `COMMITMENTS.md`) | `reviewer-physics` + `reviewer-critical` + `reviewer-constructive` → `arbiter` (arbiter audits the `[x]`/`[D]`/`[ ]` ledger) |

`reviewer-physics` is **blinded**: hand it only the artifact and the physics
question — never the methodology rationale or the other reviewers' notes.
`reviewer-critical` gets full context and must ground every number in a live
tool call. Use `plot-validator` for any figure before a reviewer opines on
it; its red flags are **not downgradable** by the arbiter.

## Iteration caps and the fresh-reviewer rule

The panel runs review → fix → re-review until no Category A remains, capped
by artifact size:

- **3** iterations — a single plot/figure.
- **5** iterations — a notebook or short analysis.
- **10** iterations — a full analysis note or repo.

**Fresh-reviewer rule:** each iteration uses a *fresh* reviewer context (a
new disposable subagent with no memory of prior rounds) to avoid anchoring
on earlier verdicts. Pass the reviewer the current artifact and question
only — not the previous findings.

If the cap is reached with a Category A still open, the arbiter ESCALATEs
rather than looping further.

## Running the panel (orchestrator steps)

1. Identify the artifact type → pick the panel from the table.
2. If a figure is in scope, run `plot-validator` first (see that skill);
   keep its report.
3. Spawn each reviewer as a subagent (task tool), giving each ONLY what its
   role allows (`reviewer-physics`: artifact + question, nothing else).
   Collect each reviewer's text findings.
4. Hand the collected findings + the `plot-validator` report + any
   `COMMITMENTS.md` to the `arbiter`. Do not pre-filter or soften findings.
5. Relay the arbiter's verdict. On ITERATE, apply the fix, then re-review
   with a FRESH reviewer (respect the cap). On ESCALATE, surface to the
   human with the deciding findings.

## COMMITMENTS.md ledger

When an analysis ships a `COMMITMENTS.md`, it uses three states: `[x]`
resolved, `[D]` formally downscoped (with justification + deadline), `[ ]`
open. The arbiter counts them and ESCALATEs when `[D]` outnumbers `[x]` — a
sign the analysis is being defined down rather than finished — even if no
single finding is independently blocking.

## Output the user sees

Relay the arbiter's block verbatim (VERDICT / RATIONALE / COMMITMENTS AUDIT
/ OPEN CATEGORY A / MUST-FIX / STYLE / IF ITERATE). Cite agent and skill
names (`reviewer-physics`, `plot-validator`, …) so the user can re-invoke
them; never quote internal `reference/` paths in the reply.

## Scope boundary

This panel reviews analysis **content**. It is not the
`verification-before-completion` gate (that blocks a "the job finished"
claim until you show `reana-client status` / exit codes / file sizes — a
different question), and it is not `read-publication` (extracting a value
from one paper). Reviewers obey the critical rules verbatim: no fabricated
numbers, cite tool calls, never approve without fresh evidence.
