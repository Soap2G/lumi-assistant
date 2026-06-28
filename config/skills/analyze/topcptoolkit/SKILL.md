---
name: topcptoolkit
description: Use when the user wants to configure, drive, or debug a run of TopCPToolkit — the ATLAS ntuple-production framework (`atlas/amg/software/TopCPToolkit`) that runs the Combined-Performance (CP) algorithms (object calibrations, systematic uncertainties, overlap removal, scale factors, selections) over DAOD_PHYS / PHYSLITE and writes analysis ntuples. Covers writing or fixing the block-based YAML config (the `Electrons`, `Muons`, `Photons`, `Taus`, `Jets`, `Tracks`, `MissingET`, `Trigger`, `Overlap`, `ObjectSelection`, `EventScaleFactors`, `EventSelection`, `Reconstruction`, `Truth`, `Output`/ntupling blocks and the global config flags), the universal per-block flags (`skipOnData`, `skipOnMC`, `onlyForDSIDs`, `propertyOverrides`), running the driver `runTop_el.py -i inputs.txt -o output [-t <config>] [--no-systematics] [-e N] [--parton --particle]`, defining object/event selections and the output ntuple branches, enabling systematics, running detector/particle/parton level, or submitting to the grid. Answers come from the canonical TopCPToolkit MkDocs documentation via the `cerndocs` MCP — `search_docs(query, source="topcptoolkit")` then `fetch_doc(url, source="topcptoolkit")`; a page map is baked into `reference/page-map.md` (also the WebFetch fallback). TopCPToolkit is version-soft: it tracks ATLAS release 25 and its CP-algorithm block/flag names evolve — verify against the user's built version and the changelog, never from memory. Does NOT cover: HISTOGRAMMING the produced ntuples / making fit inputs — regions, variables, TRExFitter configs (use `fastframes`, the downstream framework); reading a DAOD/ntuple branch directly in Python with uproot (use `physlite-basics`); getting the DAOD_PHYS/PHYSLITE files onto disk or the grid, replicas, rules (use `rucio`); ATLAS sample cross-section / sumOfWeights / DSID metadata (use `atlas-opendata`); generic Athena / ASG release or CP-tool service documentation unrelated to the TopCPToolkit config (use `cern-docs`, source atlas-sft); configuring an event generator that produced the input (Sherpa → `sherpa-manual`, MadGraph → `madgraph`); raw HTCondor/grid batch operations unrelated to TopCPToolkit's own grid runner (use `htcondor`). Disambiguator phrase: TopCPToolkit runTop_el.py and the CP-algorithm YAML config.
data_scope: both
experiment: atlas
---

# topcptoolkit — TopCPToolkit configuration & reference

TopCPToolkit (`atlas/amg/software/TopCPToolkit`) is an ATLAS **ntuple-production
framework** for Run 2 / Run 3 analyses. It runs the shared **Combined-Performance
(CP) algorithms** — object calibrations, systematic uncertainties, overlap
removal, scale factors, and object/event selection — over **DAOD_PHYS /
PHYSLITE** inputs and writes **analysis ntuples** (with CutBookkeeper metadata).
It is steered by a **block-based YAML config** and run with the `runTop_el.py`
driver. This skill covers **configuring and driving TopCPToolkit** — the CP
blocks, the driver options, the run levels, and the grid hand-off.

TopCPToolkit is the **upstream** of FastFrames: it *produces* the ntuples;
**`fastframes`** *histograms* them and writes the TRExFitter inputs. If the user
is histogramming / defining regions, that is `fastframes`, not this skill.

Upstream documentation (pinned): `https://topcptoolkit.docs.cern.ch/latest/`
(Material for MkDocs).

> **Version note — read before answering.** TopCPToolkit is **version-soft**: it
> tracks ATLAS **release 25** and its CP-algorithm block names, flags, and
> defaults evolve. Do not quote a block/flag/default as the user's — verify
> against their built version and the `changelog/`. Fabricating a CP-block key is
> a critical-rule-1 violation.

## When to load this skill

The user wants to **configure, drive, or debug TopCPToolkit itself**:

- "Write me a TopCPToolkit YAML config to calibrate electrons, muons, and jets and write a ttbar ℓ+jets ntuple."
- "Which block configures jet calibration / b-tagging working points / the MET term?"
- "How do I turn systematics on/off, and what does `--no-systematics` do?"
- "Run `runTop_el.py` over my PHYSLITE list, detector + particle level, 100 events."
- "What do `skipOnData` / `skipOnMC` / `onlyForDSIDs` / `propertyOverrides` do on a block?"
- "Define an object selection and an event selection; how do I pick the output ntuple branches?"
- "How do I submit a TopCPToolkit production to the grid?"

Do NOT load this skill for:

- **Histogramming the produced ntuples** — regions, variables, systematics
  *propagation*, cutflows, unfolding inputs, or a **TRExFitter** config →
  **`fastframes`** (the downstream framework). TopCPToolkit makes the ntuple;
  FastFrames turns it into histograms. The split is the #1 boundary.
- **Reading a DAOD / ntuple branch in Python** with uproot → **`physlite-basics`**.
- **Getting the DAOD_PHYS / PHYSLITE onto disk or the grid** — replicas, rules,
  `rucio did`/`rule` → **`rucio`**. TopCPToolkit *consumes* a file list; staging
  the files is `rucio`.
- **ATLAS sample metadata** — a DSID's cross-section, k-factor, filter
  efficiency, sumOfWeights → **`atlas-opendata`**.
- **Generic Athena / ASG / CP-tool service docs** not about the TopCPToolkit
  config (how an ASG release is built, Athena internals) → **`cern-docs`**
  (source `atlas-sft`). This skill is the *TopCPToolkit config*; the broader
  software stack is `cern-docs`.
- **The event generator** that produced the input → Sherpa **`sherpa-manual`**,
  MadGraph **`madgraph`** (far upstream — they make the events that were then
  reconstructed into the DAOD).
- **Raw HTCondor / grid batch operations** unrelated to TopCPToolkit's own grid
  runner — `condor_q`, held jobs → **`htcondor`**.

## Availability — built from source off an ATLAS release

TopCPToolkit is **not** an LCG-view tool and **not** a single binary. It is set up
from an ATLAS **AnalysisBase / Athena release 25** (`asetup`) and **built from
source**; `runTop_el.py` exists after compilation. Confirm a built + set-up
install before telling the user to run it:

```bash
setupATLAS                         # is the ATLAS setup available? (lxplus / CVMFS)
asetup AnalysisBase,25.2.XX        # <ver> per the TopCPToolkit installation page / changelog
# build the package (cmake/make per starting/installation/), then:
source <BUILD>/setup.sh
command -v runTop_el.py            # the driver, on PATH after build + setup
```

The exact release and build steps are version-soft — fetch
`starting/installation/` and confirm against the user's checked-out tag. Because
this is tool-specific (the release↔TopCPToolkit pairing comes from its docs, not
shared LCG infrastructure), it lives **here**, not in `lcg-stacks.md`. Do not
paste a fixed release as if it were current.

## Retrieval architecture (how this skill answers)

The docs are a **MkDocs** site registered in the `cerndocs` MCP as source
**`topcptoolkit`**. Primary mechanism: the MCP.

1. **`search_docs(query, source="topcptoolkit")`** — BM25 hits (title/url/snippet).
   Map the question to a block: object calibration → `settings/<object>/`;
   selection → `settings/objectselection/` or `eventselection/`; output branches
   → `settings/ntupling/`; running → `starting/running_local/` or
   `running_grid/`; first config → `tutorials/write_config/`.
2. **`fetch_doc(url, source="topcptoolkit", mode="outline"|"sections:<h>"|"markdown")`**
   for the body. If `fetch_doc` cannot resolve the versioned `/latest/` path,
   **`WebFetch`** the public URL from `reference/page-map.md` instead (always works).
3. **Cite the public `…/latest/…` URL.**
4. If the MCP source is unavailable, fall back entirely to `WebFetch` over the
   baked page map (`reference/page-map.md`); `WebSearch:
   site:topcptoolkit.docs.cern.ch <query>` if the page is unclear.

Trust order: the user's built TopCPToolkit behaviour / error output / generated
config > the `/latest/` docs > web. Version-soft — the installed release wins on
live values.

## The config at a glance (block-based YAML)

TopCPToolkit's YAML is a set of **CP-algorithm blocks**, each configuring one
object or step. The blocks (verify names against `settings/`):

| Block | Configures |
|---|---|
| config flags | global run flags (`settings/configflags/`) |
| `Electrons` / `Muons` / `Photons` / `Taus` | per-object calibration, ID/iso WPs, systematics |
| `Jets` | jet collection, calibration, JVT, b-tagging WPs |
| `Tracks` | track/vertex handling |
| `MissingET` | MET term build |
| `Trigger` | trigger selection & SFs |
| `Overlap` | overlap removal between objects |
| `ObjectSelection` | per-object kinematic/quality selection |
| `EventScaleFactors` | event-level scale factors |
| `EventSelection` | event-level selection (regions/filters) |
| `Reconstruction` | event reconstruction (e.g. tops, spin) |
| `Truth` | truth-content / particle & parton level |
| `Output` (ntupling) | which branches/variables land in the ntuple |

Universal per-block flags: `skipOnData`, `skipOnMC`, `onlyForDSIDs`,
`propertyOverrides` (expert-only). Always `search_docs`/`WebFetch` the specific
`settings/<block>/` page and quote exact keys — do not emit a CP-block key from
memory.

## Workflow — the commands (the `runTop_el.py` driver)

```bash
# inputs.txt = a text file of DAOD_PHYS / PHYSLITE file paths (ONE sample at a time).

# Minimal: default settings, detector level.
runTop_el.py -i inputs.txt -o output
#   -> output.root (ntuple + CutBookkeeper metadata histograms)

# With a named text/YAML config folder:
runTop_el.py -i inputs.txt -o output -t exampleTtbarLjets

# Quick test: limit events, skip systematics.
runTop_el.py -i inputs.txt -o output --no-systematics -e 100

# Add analysis levels (truth):
runTop_el.py -i inputs.txt -o output --parton --particle
```

| Flag | Meaning |
|---|---|
| `-i` | input file list (one sample at a time) |
| `-o` | output base name (`output.root`) |
| `-t` / `--text-config` | YAML config folder name |
| `-e` / `--max-events` | event limit |
| `--no-systematics` | disable systematic variations |
| `--parton` / `--particle` | enable parton / particle-level analysis |

Grid running is `starting/running_grid/` (+ the `tutorials/submit_grid/`
tutorial). The output ntuples are the **input to FastFrames** (`fastframes`).

Placeholders: `<BUILD>` = the build dir; never invent a real path or DSID.

## Honesty rules (specific to this skill)

- **Never quote a CP-block name, flag, working point, or default as the user's
  value.** The schema is version-soft — `search_docs`/`WebFetch` the
  `settings/<block>/` page and quote with the source, or read the user's own
  config. Fabricating a key is a critical-rule-1 violation.
- **Hold the downstream boundary.** Histogramming / regions / TRExFitter inputs
  are **`fastframes`**, not here. Don't drift into them.
- **Sample-metadata and file-staging are not config.** DSID x-sec →
  `atlas-opendata`; getting the DAOD → `rucio`.
- **Do not hard-code the environment.** Setup is `asetup` of an ATLAS release 25
  (version per the docs) + a from-source build — never a pasted fixed release.

## Output rules

- `reference/page-map.md` is a loading instruction for you, not a citation; never
  quote its path. Cite the public `…/latest/…` URL.
- Emit valid, paste-ready YAML config blocks and exact `runTop_el.py` command
  lines. Say where a key came from (the `settings/<block>/` page, or the user's
  own config).
- Cite the skill name (`topcptoolkit`) so the user can re-prompt.

## Version-bump procedure

The pin is the docs `/latest/` channel; the framework is version-soft.

1. On a release that changes the CP-block set or page structure, **re-snapshot
   the page map** (GET `<base>sitemap.xml`, regenerate `reference/page-map.md`)
   and re-confirm the block table against `settings/`.
2. The MCP source (`topcptoolkit` in `docs_sources.json`) auto-tracks `/latest/`
   via the 24 h index TTL — no per-release MCP edit needed unless the docs host
   moves.
3. Update the version-soft banner if the recommended `asetup` release moved.
4. Bump `VERSION` (patch for a page-map refresh; minor if coverage changes) and
   re-run `lint.py` + `run.py`.
