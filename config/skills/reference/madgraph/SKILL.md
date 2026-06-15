---
name: madgraph
description: Use when the user wants to configure, set up, drive, or debug a run of the MadGraph5_aMC@NLO (MG5_aMC) event generator and its integrated chain — writing `.mg5` script files (`import model`, `generate` / `add process`, `output`, `launch`), editing the cards (`run_card.dat`, `param_card.dat`, `madspin_card.dat`, `pythia8_card.dat`, `delphes_card.dat`), process syntax (multiparticle labels, decay chains, `@N` tags, diagram filtering with `/` `$` `$$`), LO vs NLO (`[QCD]` / `[QED]`, MC@NLO, FxFx / MLM matching & merging, DJR validation), models & restrictions (sm, heft, loop_sm, BSM / UFO, SMEFT), MadSpin / MadWidth decays, PDFs & scales (LHAPDF, 4F/5F schemes), parameter scans, systematics & reweighting, the Pythia8 / Delphes / MadAnalysis5 interfaces, or interpreting MG5_aMC output (LHE structure, the `Events/run_01/` layout, the cross-section banner). Answers come from a curated MadGraph documentation corpus vendored from MadGraphTeam/MadAgents (MIT, arXiv:2601.21015) and read directly from this skill's `reference/`. MG5_aMC docs are version-soft: ALWAYS verify numeric defaults (LHAPDF set IDs, default masses, widths, run_card defaults) against the user's actual installation, never from memory. Does NOT cover: ATLAS Open Data metadata for an already-produced MadGraph sample — a `MG_…` / `aMC…` `physics_short`, its DSID, cross-section, k-factor, filter efficiency, or sumOfWeights (use `atlas-opendata`); reading MadGraph's LHE output in Python (use `pylhe`) or its HepMC output (use `pyhepmc`); configuring the Sherpa generator (use `sherpa-manual`); standalone Pythia8 / Herwig tunes unrelated to the MG5 chain (not yet covered — do not answer from memory); getting `mg5_aMC` onto PATH / which LCG view to source (that is environment setup, not config); CERN batch / grid submission of a MadGraph job (use `cern-docs` source `batch`, or `htcondor`); canonical particle masses / widths as physics constants (use `pdg-lookup`). Disambiguator phrase: mg5_aMC script and card configuration.
data_scope: both
experiment: all
---

# madgraph — MadGraph5_aMC@NLO configuration & reference

MadGraph5_aMC@NLO (MG5_aMC) is a framework for automated Monte Carlo
simulation of particle-physics processes at leading order (LO) and
next-to-leading order (NLO) in QCD. It generates matrix elements, performs
phase-space integration, and produces parton-level events in Les Houches
Event (LHE) format. Combined with Pythia8 (parton shower / hadronization),
Delphes (fast detector simulation), and analysis tools, it provides a
complete chain from Lagrangian to reconstructed events. This skill covers
**configuring and driving MG5_aMC** — the `.mg5` script, the cards, the
process syntax, the parameter groups, and the chain interfaces.

Documentation corpus (pinned snapshot): `MadGraphTeam/MadAgents`
@ `cf387c2c` (MIT; arXiv:2601.21015). The 27 curated topic files live in
this skill's `reference/` (the pin is recorded in `reference/_PROVENANCE.md`).
Read them directly — that is the retrieval mechanism (no MCP, no web index).

> **Version note — read before answering.** The vendored docs target
> **MG5_aMC v3.x** and are deliberately **version-soft**: LHAPDF set IDs,
> default particle masses and widths, and `run_card.dat` defaults vary across
> MG5_aMC versions, model versions, and PDF installations. **Never quote a
> numeric default from memory or from the docs as if it were the user's
> value** — verify it against the actual installation (`lhapdf list` for PDF
> IDs, `param_card_default.dat` for masses, the generated `run_card.dat` for
> run defaults). This is Lumi critical rules 1 & 6 applied to MadGraph.

## When to load this skill

The user wants to **configure, drive, or debug MG5_aMC itself**:

- "Write me a `.mg5` script to generate `p p > t t~` at NLO and shower with Pythia8."
- "What's the process syntax for a decay chain / multiparticle label / `@N` tag?"
- "How do I set up FxFx (or MLM) merging, and how do I read the DJR plots?"
- "Which `run_card.dat` parameter controls `ebeam`, `nevents`, the dynamical scale?"
- "How do I import a UFO/BSM model, or apply a SMEFT restriction file?"
- "Set up a parameter scan over a coupling; how does `scan:` syntax work?"
- "Turn on scale/PDF systematics and get the uncertainty envelope."
- "I ran MG5 and got `Events/run_01/` with an LHE file and a cross-section banner — what's in them?"

Do NOT load this skill for:

- **Metadata of an already-produced MadGraph sample** — a `physics_short`
  beginning `MG` (MadGraph LO) or `aMC` (aMC@NLO), its DSID, cross-section,
  k-factor, filter efficiency, or sumOfWeights → **`atlas-opendata`**. (Those
  abbreviations mean "produced *by* MadGraph"; that is a catalogue lookup, not
  generator config — the exact analogue of the `Sh_…`/`sherpa-manual` split.)
- **Reading MG5_aMC's output files** in Python — Les Houches Event (LHE)
  files → **`pylhe`**; HepMC records (after showering) → **`pyhepmc`**. This
  skill explains the *format*; reading it in code is those skills.
- **The Sherpa generator** → **`sherpa-manual`**. The two are confusable
  ("generate Z+jets"); the *generator named* decides. If the user has not said
  which, ask.
- **Standalone Pythia8 / Herwig tuning** unrelated to the MG5 chain (a bare
  Pythia8 hadronization tune) → not yet covered by lumi; say so and stop. The
  `pythia8-interface.md` here is specifically the **MG5→Pythia8** interface.
- **Getting `mg5_aMC` onto PATH** ("command not found", "which LCG view") →
  **environment setup**, not config; see Availability below — never a
  hard-coded path.
- **CERN batch / grid submission** of a MadGraph job ("submit it to lxbatch")
  → **`cern-docs`** (`source=batch`) or **`htcondor`**.
- **Canonical particle constants** (a mass/width as a physics *fact*, not a
  card default) → **`pdg-lookup`**.
- **An autonomous, multi-step run→verify→iterate MadGraph *campaign*** (let an
  agent install MG5, run it, check the cross-section by execution, and loop) →
  that is **MadAgents** itself (the agent framework this corpus is vendored
  from; arXiv:2601.21015), not this skill. Lumi *advises* on config and
  *explains* output; it does not drive the generator. Say so and point there.

## Availability — the `mg5_aMC` binary

This skill answers documentation/config questions without the binary. When the
user wants to actually *run* a setup, check:

```bash
command -v mg5_aMC        # is the executable on PATH?
```

MG5_aMC reaches a host two common ways:

1. **A standalone install** — the user downloaded the tarball and runs
   `<MG5_DIR>/bin/mg5_aMC`. Setup, dependencies, and the `install` command
   (Pythia8 / Delphes / MadAnalysis5) are in `reference/installation.md`.
2. **An LCG view on CVMFS** (at CERN) — sourcing a view puts `mg5_aMC` on
   PATH. The exact stack/platform are **intentionally not hard-coded here**
   (they bump independently of this corpus): the single source of truth is
   `config/skills/infra-advisor/reference/lcg-stacks.md`, and the mechanism is
   in AGENTS.md "## Environment". Do **not** paste an `LCG_<NNN>` path into
   this skill.

If `command -v mg5_aMC` finds nothing, the user must install it (path 1) or
source a view (path 2) — do not answer "run it" until one is confirmed. The
installed **version** matters because the docs are version-soft: confirm it
(e.g. the banner printed at the top of an `mg5_aMC` session) before quoting
any numeric default.

## Retrieval architecture (how this skill answers)

The corpus is a **constant**: 27 curated topic files in `reference/`. There is
no MCP and no vector store; you **Read the relevant file directly**. Mirror the
upstream operator's trust hierarchy:

1. **Map the question to a topic file** using the index below, and **Read**
   `reference/<topic>.md`. Quote the relevant syntax / parameter.
2. **Trust the installation over the docs for live values.** Code output,
   error messages, generated cards, and the MG5_aMC Python source are
   authoritative for *this* install; the docs are the map, not the territory.
3. **Web search is a last resort** — be skeptical, prefer official
   MadGraph / Launchpad sources, and cross-check against the local corpus.

If sources disagree: MG5_aMC source/behaviour > local corpus > web.

## Quick start — script-based execution

Save as `ttbar.mg5` and run with `<MG5_DIR>/bin/mg5_aMC ttbar.mg5`:

```
import model sm
generate p p > t t~
output ttbar_LO
launch ttbar_LO
  set run_card ebeam1 6500
  set run_card ebeam2 6500
  set run_card nevents 10000
  done
```

This generates 10,000 LO t-tbar events at 13 TeV; results appear in
`ttbar_LO/Events/run_01/`. **Script-first** is the convention throughout the
corpus — prefer a runnable `.mg5` file over interactive-prompt instructions
unless the user explicitly wants interactive mode (`reference/interactive-mode.md`).

## The simulation chain

```
Hard process — matrix elements, LHE events (MadGraph5)
  → Parton shower — shower, hadronization, underlying event (Pythia8, Herwig7, …)
  → Detector simulation — fast/full detector response (Delphes, Geant4, …)
  → Analysis — cuts, histograms, signal regions (MadAnalysis5, Rivet, …)
```

Plug-ins: **MadSpin** (spin-correlated decays, between hard process and
shower), **MadWidth** (decay-width computation).

## Topic index — which `reference/` file governs what

Map the user's intent to a file, then **Read** `reference/<file>.md`.

### Getting started
| Topic | File |
|---|---|
| Install, dependencies, `install` command | `installation.md` |
| `generate` / `add process`, multiparticle labels, decay chains, `@N` | `process-syntax.md` |
| Built-in models (sm, heft, loop_sm), BSM/UFO imports, restriction files | `models-and-restrictions.md` |
| `param_card`, `run_card`, generation-level & custom cuts | `cards-and-parameters.md` |
| Script-mode workflow, `launch` options, gridpacks, `compute_widths` | `scripted-execution.md` |
| Interactive MG5 prompt commands & navigation | `interactive-mode.md` |

### NLO & matching/merging
| Topic | File |
|---|---|
| NLO QCD/EW (`[QCD]`/`[QED]`), MC@NLO, `mcatnlo_delta`, FKS | `nlo-computations.md` |
| MadSTR (DR/DS), loop-induced + jets, squared orders, flavor schemes | `nlo-plugins-and-loops.md` |
| MLM (`xqcut`/`qCut`), FxFx, CKKW-L, DJR validation plots | `matching-and-merging.md` |
| `QCD=`/`QED=`, squared orders (`^2==`), automatic ordering, x-sec checks | `coupling-orders-and-validation.md` |

### Decays & widths
| Topic | File |
|---|---|
| Decay methods (syntax / MadSpin / MadWidth), `spinmode`, `compute_widths` | `decays-and-madspin.md` |
| Complex mass scheme, NWA validity, width consistency | `complex-mass-scheme.md` |

### Simulation chain
| Topic | File |
|---|---|
| Shower settings, `pythia8_card`, tune selection, jet matching in Pythia8 | `pythia8-interface.md` |
| Fast detector sim, detector cards, shower/detector consistency | `delphes-interface.md` |
| Analysis-framework integration, cut definitions, histogram output | `madanalysis5.md` |
| LHE event-file structure, particle records, weights, Python parsing | `lhe-output-format.md` |

### Physics inputs
| Topic | File |
|---|---|
| PDF selection, LHAPDF, dynamical scales, 4F/5F flavor schemes | `pdfs-and-scales.md` |
| `scan:` syntax, Cartesian/correlated scans, thread-leak workaround | `parameter-scans.md` |
| `lpp` settings, beam polarization, EPA, muon colliders | `lepton-photon-colliders.md` |
| `use_syst`, `systematics` module, scale/PDF uncertainty envelopes | `systematics-reweighting.md` |

### Advanced & troubleshooting
| Topic | File |
|---|---|
| `/`, `$`, `$$` operators, s-channel filtering, resonance selection | `diagram-filtering.md` |
| `bias` module, `ptj_bias`, custom bias functions | `biased-event-generation.md` |
| Dimension-6 operators, restriction files, interference isolation | `eft-smeftsim.md` |
| Relic density, direct/indirect detection, co-annihilation | `maddm-dark-matter.md` |
| MadDM parameter cards, scan configuration, output | `maddm-cards-and-scans.md` |
| Fortran/C++/Python standalone ME output, external evaluation | `standalone-matrix-elements.md` |
| Common errors, integration problems, numerical instabilities | `troubleshooting.md` |

## Key conventions (from the curated corpus)

- **Script-first.** Show runnable `.mg5` files (`<MG5_DIR>/bin/mg5_aMC script.mg5`)
  unless interactive mode is explicitly wanted.
- **Placeholders.** `<PROC_DIR>` = a user-chosen process/output directory;
  `<MG5_DIR>` = the MadGraph install directory. Never invent a real path.
- **Verify numeric values.** LHAPDF IDs, default masses, widths, and other
  numeric parameters differ across MG5_aMC / model / PDF versions. Verify
  against the current installation — `lhapdf list`, `param_card_default.dat`,
  the generated `run_card.dat`.
- **Version.** Corpus targets MG5_aMC v3.x; version-specific differences are
  noted in the files where they matter.

## Honesty rules (specific to this skill)

- **Never quote a numeric default as the user's value.** Card defaults, PDF
  IDs, masses, and widths are installation-dependent — verify, then quote with
  the source ("from your generated `run_card.dat`"). Fabricating one is a
  critical-rule-1 violation.
- **Do not invent process syntax, card keys, or model names.** Read the topic
  file and quote it; MG5_aMC has many near-miss spellings.
- **`MG_…`/`aMC…` sample questions are not config questions.** A
  cross-section / DSID for a produced sample is **`atlas-opendata`**; redirect.
- **Stay inside the MG5 chain.** A Sherpa question → `sherpa-manual`; a bare
  Pythia8 tune unrelated to MG → not covered; say so.
- **Do not hard-code the environment.** "How do I get `mg5_aMC`" is answered
  via `command -v mg5_aMC` + `installation.md` + the centralized LCG
  reference, never a pasted `LCG_<NNN>` path.

## Output rules — what makes it into the user reply

- The `reference/*.md` files are **loading instructions for you, not citations
  for the user** (AGENTS.md output rules). Never quote a `reference/…md` path
  in a reply — Read it silently and synthesise.
- Emit runnable `.mg5` script blocks and exact card lines the user can paste.
- When you state a default or a numeric value, say where it came from (the
  topic file as guidance, or — preferred — the user's own installation).
- Cite the skill name (`madgraph`) so the user can re-prompt; cite the public
  MadGraph project / Launchpad URL only when pointing at upstream detail beyond
  the corpus.

## Version-bump procedure

The pin is the **snapshot SHA** (corpus provenance), not a MadGraph version.

1. To refresh the corpus: bump `SHA` + `DATE` in
   `script/vendor/snapshot_madgraph_docs.sh`, add/remove `FILES` basenames if
   upstream changed its topic set, re-run it, and review the diff. Update
   `reference/_PROVENANCE.md` with the new pin. (This is a deliberate pull — the
   corpus is intentionally not in `sync_vendored.py --check`.)
2. If the upstream topic set changed, update the **Topic index** table above
   and the README enumeration to match.
3. If MG5_aMC's shipped version in the LCG stack moved, update the `mg5_aMC`
   row in `infra-advisor/reference/lcg-stacks.md` (the docs are version-soft,
   so usually no skill-body edit is needed — but re-confirm the quick-start
   still runs).
4. Bump `VERSION` (patch for a corpus refresh; minor if the skill's coverage
   changes) and re-run `lint.py` + `run.py`.
