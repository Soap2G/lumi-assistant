---
name: sherpa-manual
description: Use when the user wants to configure, set up, debug, or understand a run of the Sherpa Monte Carlo event generator (v3.0.1, the version in the current CERN LCG stack) — writing or fixing the `Sherpa.yaml` YAML steering file, defining the `PROCESSES` block with PDG codes and particle containers, choosing matrix-element generators (Comix / Amegic), parton showers, multijet merging (MEPS@NLO / CKKW) or NLO matching (MC@NLO), beams / PDFs / scale variations / selectors, hadronization, hard decays, or the `Sherpa` command-line options (`-e`, `-p`, `-a`, `-R`, …). Answers come from the canonical Sherpa v3.0.1 manual (a Sphinx site) via WebFetch; the page map is baked in. CRITICAL: Sherpa v3 uses YAML steering (`Sherpa.yaml`) — NOT the legacy v2 `Run.dat` `(run){…}(end)` syntax, and v2 steering files are not reusable. Does NOT cover ATLAS Open Data Sherpa-produced sample metadata — DSIDs, `physics_short` names like `Sh_2211_Zee_…`, cross-sections, k-factors, sumOfWeights (use `atlas-opendata`); reading Sherpa's HepMC3 output event records (use `pyhepmc`) or Les Houches Event files (use `pylhe`); how to get the Sherpa binary on PATH / which LCG view to source (that is environment setup, not config); other generators Pythia / Herwig / MadGraph / Powheg (not yet covered); or CERN service / batch / grid documentation (use `cern-docs`). Disambiguator phrase: Sherpa.yaml steering configuration.
data_scope: both
experiment: all
---

# sherpa-manual — Sherpa v3.0.1 generator configuration & reference

Sherpa (Simulation of High-Energy Reactions of PArticles) is a multipurpose
Monte Carlo event generator. This skill covers **configuring and understanding
a Sherpa run** — the steering file, process setup, and the parameter groups —
grounded in the canonical v3.0.1 manual.

Upstream manual (pinned): https://sherpa-team.gitlab.io/sherpa/v3.0.1/

> **Version banner — read before answering.** Sherpa **v3** is steered by a
> **YAML** file named `Sherpa.yaml`. This is a hard break from **v2**, whose
> setups used a `Run.dat` file with `(run){ … }(end)` / `(processes){ … }(end)`
> blocks. The v3 manual states plainly that **steering files from previous
> versions are not reusable**. Training-data memory of Sherpa is mostly the v2
> `Run.dat` syntax — do not emit it. When a user pastes a v2 `Run.dat`, treat it
> as a *port* request, not a copy-paste.

## When to load this skill

The user wants to **configure or understand Sherpa itself**:

- "Write me a `Sherpa.yaml` to generate Z→ee + up to 4 jets with MEPS@NLO."
- "What's the `PROCESSES` syntax for pp → t t̄ in Sherpa v3? Which PDG codes?"
- "Which command-line flag sets the number of events / the run directory?"
- "How do I turn on hard decays with branching-ratio reweighting?"
- "What does `CKKW` / the merging scale do in the process block?"
- "I have a Sherpa v2 `Run.dat` — port it to v3 YAML."
- "How do I pick the PDF set / scale variations / a phase-space selector?"

Do NOT load this skill for:

- **Metadata of an already-produced Sherpa sample** — a `physics_short` like
  `Sh_2211_Zee_maxHTpTV2_BFilter`, its DSID, cross-section, k-factor,
  filter efficiency, or sumOfWeights → **`atlas-opendata`**. (The `Sh` prefix
  means "produced *by* Sherpa"; that is a catalogue lookup, not generator
  config.)
- **Getting the Sherpa binary onto PATH** ("Sherpa: command not found", "which
  LCG view do I source") → that is **environment setup**, not config; see the
  Availability section below — do not answer it from a hard-coded path.
- **Reading Sherpa's output event files** in Python — HepMC3 records →
  **`pyhepmc`**; Les Houches Event (LHE) files → **`pylhe`**.
- **A different generator** — Pythia, Herwig, MadGraph, Powheg, alpgen. Not yet
  covered by lumi; do not answer from memory. Say so and stop.
- **CERN service / batch / grid documentation** ("how do I submit the Sherpa job
  to lxbatch") → **`cern-docs`** (`source=batch`) or `htcondor`.
- **Canonical particle constants** (a mass / width to put in a model) →
  **`pdg-lookup`**.

## Availability — the Sherpa binary

This skill answers documentation/config questions without needing the binary.
When the user wants to actually *run* a setup, **probe it functionally** — source
the view and ask Sherpa for its version, in one command (`command -v Sherpa` only
proves it is on PATH, not that it runs):

```bash
source /cvmfs/sft.cern.ch/lcg/views/<STACK>/<PLATFORM>/setup.sh && Sherpa --version
```

A printed `Sherpa version …` banner means it is runnable. If instead you get
`error while loading shared libraries: libSherpa*.so`, the view did not put
Sherpa's lib dir on `LD_LIBRARY_PATH` — this is a known runtime quirk, not an
absent install. Fix it (then re-probe):

```bash
export LD_LIBRARY_PATH="$(Sherpa-config --prefix)/lib64/SHERPA-MC:$LD_LIBRARY_PATH"
```

If `command -v Sherpa` finds nothing at all, the user has not set up their
software environment. At CERN, Sherpa is provided by an **LCG view** on CVMFS —
the user sources the view, then re-probes. The exact stack and platform are
**intentionally not hard-coded here** (they bump independently of the manual):
the single source of truth — including the runtime-quirk fix above — is
`config/skills/infra-advisor/reference/lcg-stacks.md`, and the mechanism is in
AGENTS.md "## Environment". Do **not** paste a `LCG_<NNN>` path into this skill.

Runtime vs. docs: the current LCG stack ships Sherpa **3.0.1p2**; this skill is
pinned to the **v3.0.1** manual (the closest published manual — the `pN` patch
tags have no separate manual). If the stack later ships a minor/patch that
crosses a docs boundary, follow the Version-bump procedure below.

## Retrieval architecture (how this skill answers)

The manual is a **Sphinx** site. Its structure is a **constant** for v3.0.1 and
is baked into `reference/page-map.md` (36 pages + 24 command-line options +
key section anchors). Do **not** re-derive it, and do **not** build any index.

1. **Map the question to a page** using the page map below (or the fuller table
   in `reference/page-map.md`).
2. **`WebFetch`** that page's `…/v3.0.1/…html` URL, passing the user's question
   as the fetch prompt. Quote the relevant prose.
3. **Cite the public v3.0.1 URL** so the user can open it.
4. If the right page is unclear, fall back to
   `WebSearch: site:sherpa-team.gitlab.io/sherpa/v3.0.1 <query>`, then fetch.
   (The Sphinx `search.html?q=` page is JS-rendered and not WebFetch-friendly.)

There is no MCP and no vector store. WebFetch over the pinned page map is the
whole mechanism. This is deliberate (see the skill plan's rationale).

## Steering file format (`Sherpa.yaml`) — the essentials

Default file: `Sherpa.yaml` in the current directory. Run with `Sherpa`
(the executable in `<prefix>/bin/`). Use a different directory with
`-p <dir>`; pass an alternative file as a **positional argument**:
`Sherpa myfile.yaml` (multiple files merge left-to-right, rightmost wins).
The legacy `-f <file>` / `RUNDATA: [...]` form is **deprecated** — use
positional arguments.

The file is **YAML**. Top-level settings are key-value pairs:

```yaml
EVENTS: 100M           # number of events (M/k suffixes allowed)
BEAMS: 2212            # PDG code of the beam particles (2212 = proton)
BEAM_ENERGIES: 7000    # per-beam energy in GeV
```

Some settings are **nested mappings** (block style by indentation, or flow
style with braces):

```yaml
HARD_DECAYS:
  Enabled: true
  Apply_Branching_Ratios: false
# equivalently: HARD_DECAYS: { Enabled: true, Apply_Branching_Ratios: false }
```

Some are **sequences** (dash list, or flow style with brackets); items may
themselves be sequences:

```yaml
SCALE_VARIATIONS:
  - 0.25
  - [0.25, 1.00]      # (muF, muR) pair
  - [1.00, 0.25]
# equivalently: SCALE_VARIATIONS: [0.25, [0.25,1.00], [1.00,0.25]]
```

Source: https://sherpa-team.gitlab.io/sherpa/v3.0.1/manual/input-structure.html

## The `PROCESSES` block (the #1 question)

The hard scattering process lives in the `PROCESSES` sequence. Initial/final
states are given by **PDG codes** or **particle containers** (e.g. `93` =
the light-jet container). `N{k}` requests up to `k` extra jets off that leg.
Per-process settings (coupling `Order`, merging scale `CKKW`, …) nest under
the declaration:

```yaml
PROCESSES:
  - 93 93 -> 11 -11 93{4}:        # Drell-Yan (Z/γ*→e+e-) + up to 4 jets
      Order: { QCD: 0, EW: 2 }    # coupling powers of the core process
      CKKW: 20                    # ME+PS merging (CKKW-L) scale Q_cut in GeV
```

- PDG codes: `11`/`-11` = e⁻/e⁺, `2212` = proton, `93` = light-jet container.
  See the manual's **Particle containers** section for the full list.
- A multiplicity key groups settings across jet bins, e.g. `2->2-4: { … }`.
- `Order` sets the coupling powers; `CKKW` switches on multijet merging and
  sets the merging (separation) scale.

Source: https://sherpa-team.gitlab.io/sherpa/v3.0.1/manual/parameters/processes.html

## Command-line options (verified against v3.0.1)

`Sherpa` accepts long (`--`) and short (`-`) forms. Most-used:

| Short | Long | Meaning |
|---|---|---|
| `-e <N>` | `--events` | number of events to generate |
| `-p <dir>` | `--path` | run/setup directory (also `'PATH: <dir>'`) |
| `-r <dir>` | `--result-directory` | where integration results are cached |
| `-R <seed>` | `--random-seed` | RNG seed (reproducibility) |
| `-a <list>` | `--analysis` | enable analysis handler(s) (e.g. Rivet) |
| `-A <dir>` | `--analysis-output` | analysis output directory |
| `-m <gen>` | `--me-generators` | matrix-element generator (Comix / Amegic) |
| `-s <gen>` | `--shower-generator` | parton-shower module |
| `-w <mode>` | `--event-generation-mode` | weighted / unweighted / … |
| `-l <file>` | `--log-file` | write the run log to a file |
| `-O <lvl>` | `--output` | console output verbosity |
| `-o <lvl>` | `--event-output` | event-output format/level |
| `-b` | `--disable-batch-mode` | interactive (non-batch) run |
| `-I` | `--enable-init-only` | initialise only, do not generate |
| `-v` | `--version` | print version |
| `-h` | `--help` | help |
| `-f <file>` | `--run-data` | **deprecated** — use a positional arg |

Full list (24 options incl. `-L`, `-t`, `-M`, `-F`, `-D`, `-g`, `-V`) in
`reference/page-map.md`. Source:
https://sherpa-team.gitlab.io/sherpa/v3.0.1/manual/command-line-options.html

## Parameter groups — which page governs what

`PROCESSES` aside, settings are documented per topic under
`manual/parameters/<topic>.html`. Map the user's intent to the page, then fetch:

| Topic | Page (`…/v3.0.1/manual/parameters/<x>.html`) |
|---|---|
| Beams (type, energies, structure) | `beam` |
| Initial-state radiation / PDFs | `isr` |
| Matrix elements (generator, orders, NLO) | `matrix-elements` |
| **Processes** (the hard process) | `processes` |
| Selectors (phase-space cuts) | `selectors` |
| Parton showers | `parton-showers` |
| Scales, couplings, general knobs | `general-parameters` |
| Integration / phase-space | `integration` |
| Hadronization (cluster fragmentation) | `hadronization` |
| Hard decays | `hard-decays` |
| QED corrections (YFS) | `qed-corrections` |
| Approximate EW corrections | `approximate-ew-corrections` |
| Multiple interactions (underlying event) | `multiple-interactions` |
| Minimum-bias events | `minimum-bias-events` |
| Models (SM / BSM) | `models` |
| Beam remnants / colour reconnections | `beam-remnants`, `colour-reconnections` |

Higher-level pages: `getting-started` (install + first run), `input-structure`
(the YAML rules above), `examples`, `tips-and-tricks`, `customization/*`
(external PDFs/RNG/one-loop ME, Python interface, user hooks). The complete
36-page index is in `reference/page-map.md`.

## Honesty rules (specific to this skill)

- **Never emit v2 `Run.dat` `(run){…}(end)` syntax.** If unsure whether a knob
  is spelled the same in v3, fetch the relevant page and confirm.
- **Do not invent parameter names, defaults, or values.** Sherpa has hundreds of
  settings; quote them from the fetched page, not from memory.
- **Do not hard-code the environment.** "How do I get Sherpa" is answered via
  `command -v Sherpa` + the centralized LCG reference, never a pasted
  `LCG_<NNN>` path.
- **Stay inside Sherpa.** A Pythia/Herwig/MadGraph question is out of scope.
- **Sample-metadata questions are not config questions.** "Cross-section of
  `Sh_2211_Zee…`" is `atlas-opendata`; redirect.

## Output rules — what makes it into the user reply

- Cite the **public v3.0.1 URL** of the page you used.
- Quote the relevant prose / exact setting name and YAML shape from the fetched
  page. Emit YAML the user can paste into `Sherpa.yaml`.
- When you give a `Sherpa.yaml` snippet, keep it **valid YAML** (consistent
  indentation; block or flow style, not a mix that breaks parsing).

## Version-bump procedure

When the LCG stack (or the user) moves to a different Sherpa **minor/patch** and
the manual URL changes (e.g. v3.0.1 → v3.0.5 or v3.1.x):

1. Confirm the new version in `infra-advisor/reference/lcg-stacks.md` (the LCG
   pin is the trigger; this skill follows it across docs boundaries).
2. Replace `v3.0.1` → `<new>` in the description, the body URLs, and
   `reference/page-map.md`.
3. Re-snapshot the inventory:
   `curl -s …/<new>/objects.inv` → decompress (zlib after the 4-line header) →
   regenerate the page list and command-line-option table.
4. Re-confirm the steering format on `manual/input-structure.html`.
5. Bump `VERSION` (patch) and re-run the eval harness.
