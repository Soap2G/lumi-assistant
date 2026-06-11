---
name: plot-validator
description: Use to run the deterministic red-flag checks on an analysis FIGURE — a histogram PNG/PDF or its histogram/fit JSON — before a human or a reviewer agent opines on it. The shipped `scripts/plot_checks.py` checks the file exists and is non-empty, data/MC ratios sit inside a profile's band, no empty/negative bins, the fit has positive degrees of freedom (catches `chi2/ndf = 0/0`), goodness-of-fit is acceptable, and the MeV/GeV axis-unit trap; thresholds come from `reference/thresholds.md`, not the code. Then VIEW the rendered image (PDF → text via the AGENTS.md pdftotext/pypdf recipe). NOT the multi-reviewer protocol that decides PASS/ITERATE/ESCALATE (that is `analysis-review`); NOT the compute-step completion gate (that is `verification-before-completion`). Disambiguator phrase: programmatic plot red-flag checks.
data_scope: both
experiment: all
---

## What this is

The mechanical half of figure review: the checks nobody should eyeball. It
is a *tool* the `analysis-review` panel calls before `reviewer-physics`
looks at a plot, but you can also run it standalone on any figure. Its red
flags are **not downgradable** by the `arbiter`.

Two halves, run **both**:

1. **The script** — `scripts/plot_checks.py` runs the deterministic checks.
2. **Your eyes** — view the rendered image. The script cannot see a
   mislabelled axis, a legend covering the signal, or a log/linear mistake.

## Running the script

```bash
python3 config/skills/operational/plot-validator/scripts/plot_checks.py \
    --image path/to/figure.pdf \
    --hist-json path/to/hist.json \
    --profile cross_section
```

- `--image` takes a PNG or PDF; it is checked for existence, non-zero size,
  and (PDF) extractable text.
- `--hist-json` carries the numbers — per-bin `data`/`mc`, optional `fit`
  (`chi2`, `ndf`), and `x_unit` / `x_max` / `quantity` for the unit check.
  Schema is documented in the script's header.
- `--profile` selects a threshold set: `default`, `cross_section` (tighter),
  or `search` (looser, for blinded control regions). Add profiles by editing
  `reference/thresholds.md` — **never** hard-code numbers in the script.
- Exit code is non-zero when a Category A red flag fires, so it can gate a
  pipeline.

Give it whatever you have: image only, JSON only, or both. With only an
image the quantitative checks are skipped — so still view it.

## What the checks mean

- **A — blocking:** file missing/empty; negative yields; fit `ndf <= 0`
  (the `chi2/ndf = 0/0` failure) or below `min_ndf`; data/MC out of band in
  more bins than the profile tolerates.
- **B — must-fix:** a few out-of-band bins within tolerance; empty data bins
  where the profile disallows them; poor `chi2/ndf`; the MeV/GeV
  axis-unit/scale mismatch; un-extractable PDF text.
- **C — style:** reserved for the human pass — labels, legend, aesthetics.

The numeric bounds behind A/B live in `reference/thresholds.md`. Read that
file to see or tune them; do not restate the numbers here or in the script.

## View the rendered image (always)

The script does not replace looking. Open the figure and check the things
only a human catches: axis titles and units, legend placement, log vs
linear, a ratio panel that disagrees with the main panel, a signal hidden
under a legend box. For a **PDF**, extract its text first (per AGENTS.md,
because opencode's Read returns raw bytes for PDFs):

1. `pdftotext '<path>' -` and read stdout.
2. If missing: `python3 -c "import pypdf; r = pypdf.PdfReader('<path>');
   print('\n\n'.join(p.extract_text() for p in r.pages))"`.
3. If both fail, report the actual error — do not skip the visual check
   silently.

## Output

Report each finding as `[A|B|C] <title> — <detail>` and state whether any
Category A fired (the script prints this and sets its exit code). When this
runs inside `analysis-review`, hand the full report to the `arbiter`
unmodified; its Category A flags cannot be downgraded.
