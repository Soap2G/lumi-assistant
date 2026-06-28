---
name: fastframes
description: Use when the user wants to configure, drive, or debug a run of FastFrames — the ATLAS RDataFrame-based histogramming / ntuple-reprocessing framework (`atlas-amglab/fastframes`) that turns TopCPToolkit-format Run 2/Run 3 ntuples into histograms or ntuples with systematics, cutflows, and unfolding inputs. Covers writing or fixing the YAML config (the `general`, `samples`, `regions`, `ntuples`, `systematics`, `cutflows`, `truth_processing`, `unfolding`, `simple_onnx_inference`, `numbering_sequence`, `systematic_names_mapping` blocks), running `python3 .../python/FastFrames.py -c config.yml --step h` (histograms, default) or `--step n` (ntuples), producing the input metadata (`produce_metadata_files.py` → `filelist.txt` + `sum_of_weights.txt`), defining variables/columns or a custom class (`custom_frame_name`), configuring systematics / regions / selections / luminosity / cross-section files, splitting and submitting jobs (`--samples`, `--split_n_jobs` / `--job_index`, `batch_submit.py` for HTCondor / Slurm, the grid runner), or auto-generating a TRExFitter config (`produce_trexfitter_config.py`). Answers come from the canonical FastFrames MkDocs documentation via the `cerndocs` MCP — `search_docs(query, source="fastframes")` then `fetch_doc(url, source="fastframes")`; a page map is baked into `reference/page-map.md` (also the WebFetch fallback). FastFrames is version-soft: its config schema evolves across releases — verify block/key names against the user's built FastFrames version and its changelog (and the matching `asetup StatAnalysis,<ver>`), never from memory. Does NOT cover: producing the INPUT ntuples or configuring the CP algorithms upstream — for TopCPToolkit configuration use `topcptoolkit`; running the binned-likelihood FIT in TRExFitter (FastFrames only writes the TRExFitter config + the input histograms — running the fit is separate; for open-data statistical fitting use `pyhf`); ATLAS sample metadata that FEEDS the config — a DSID's cross-section, k-factor, filter efficiency, or sumOfWeights (use `atlas-opendata`); reading a PHYSLITE / ntuple branch directly in Python with uproot (use `physlite-basics`); generic HTCondor operations unrelated to FastFrames' own `batch_submit.py` — `condor_q`, debugging a held job, `+JobFlavour` (use `htcondor`); in-memory 4-vector or jet-clustering math (use `vector` / `fastjet`); configuring an event generator (Sherpa → `sherpa-manual`, MadGraph → `madgraph`). Disambiguator phrase: FastFrames config.yml and FastFrames.py --step.
data_scope: both
experiment: atlas
---

# fastframes — FastFrames configuration & reference

FastFrames (`atlas-amglab/fastframes`) is an ATLAS analysis framework built
around ROOT's **RDataFrame**. It reprocesses **TopCPToolkit-format ntuples**
(ATLAS Run 2 / Run 3) into **histograms or output ntuples**, automating the
bookkeeping of sample definitions, weighting, systematic variations, cutflows,
and unfolding inputs, and it can auto-generate a **TRExFitter** config for the
downstream fit. The C++ core does the event loop; a Python layer
(`FastFrames.py`) steers it from a single **YAML config**. This skill covers
**configuring and driving FastFrames** — the config blocks, the run steps, the
metadata step, distributed running, and the TRExFitter hand-off.

Upstream documentation (pinned): the FastFrames MkDocs site,
`https://atlas-project-topreconstruction.web.cern.ch/fastframesdocumentation/latest/`
(BSD-2-Clause; cite Zenodo DOI 10.5281/zenodo.14773274 for the software).

> **Version note — read before answering.** FastFrames is **version-soft**:
> the config schema (block names, keys, defaults) and the recommended
> `asetup StatAnalysis,<ver>` evolve across the framework's frequent releases.
> The tutorial currently pins `v7.1.1` with `StatAnalysis,0.8.0`, but **do not
> quote a config key, default, or StatAnalysis version as the user's** — verify
> against their built FastFrames version and the **changelog**
> (`.../latest/changelog/`). Fabricating a config key is a critical-rule-1
> violation (the same discipline as not inventing physics numbers).

## When to load this skill

The user wants to **configure, drive, or debug FastFrames itself**:

- "Write me a FastFrames `config.yml` to histogram my ttbar region with nominal + JES systematics."
- "What goes in the `general` block — `input_filelist_path`, `luminosity`, `number_of_cpus`, `xsection_files`?"
- "How do I define a new variable / column in a `regions` block? Do I need a custom class?"
- "Run FastFrames in ntupling mode and only keep `jet_pt_.*` and `weight_total_.*` branches."
- "How do I produce the `filelist.txt` and `sum_of_weights.txt` metadata first?"
- "Split my samples across 20 batch jobs and submit them to HTCondor with `batch_submit.py`."
- "Turn on automatic systematics / configure `systematic_names_mapping`."
- "Generate a TRExFitter config from my FastFrames config with `produce_trexfitter_config.py`."
- "My FastFrames run crashed / produced empty histograms — help me read the config and the error."

Do NOT load this skill for:

- **Producing the INPUT ntuples** — configuring **TopCPToolkit** (CP algorithms,
  object selection, calibrations, the systematics *at ntuple-production* time) is
  upstream of FastFrames — use **`topcptoolkit`**. FastFrames *consumes* TopCPToolkit
  output; it does not make it.
- **Running the binned-likelihood FIT** — FastFrames writes the **TRExFitter
  config** (`produce_trexfitter_config.py`) and the **input histograms**, but it
  does **not** run TRExFitter or do the fit. Running TRExFitter is separate (no
  lumi skill yet — say so); for **open-data** statistical fitting use **`pyhf`**.
- **ATLAS sample metadata that feeds the config** — a DSID's cross-section,
  k-factor, filter efficiency, or sumOfWeights (the numbers that go into
  `xsection_files` / the luminosity weighting) → **`atlas-opendata`**. FastFrames
  *uses* those values; resolving them is a catalogue lookup.
- **Reading a PHYSLITE / ntuple branch directly in Python** with uproot →
  **`physlite-basics`**. This skill configures the *framework*; ad-hoc branch
  reading in your own script is that skill.
- **Generic HTCondor operations** unrelated to FastFrames' own submission wrapper
  — `condor_q`, `condor_rm`, debugging a held job, `+JobFlavour` choices →
  **`htcondor`**. FastFrames' `batch_submit.py` (its `batch_submit.yml`, sample
  splitting) is *here*; raw batch operation is `htcondor`.
- **In-memory kinematics** — a one-off invariant mass / ΔR / boost (`vector`) or
  jet clustering from constituents (`fastjet`). Defining such a quantity *as a
  FastFrames column* is here; computing it in your own array code is those skills.
- **Configuring an event generator** — Sherpa → **`sherpa-manual`**, MadGraph →
  **`madgraph`**. Those are far upstream (they make the events; TopCPToolkit then
  reconstructs them; FastFrames then histograms the ntuples).

## Availability — FastFrames is built from source off an ATLAS release

FastFrames is **not** an LCG-view tool and **not** a single binary on PATH. It is
set up from the ATLAS **StatAnalysis** release and **built from source**, then
run as a Python script. Confirm the user has a built + sourced install before
telling them to "run it":

```bash
# 1. ATLAS release (provides ROOT/RDataFrame + deps). Version is dictated by the
#    FastFrames changelog — verify, do not assume 0.8.0:
setupATLAS -q                      # is setupATLAS available? (lxplus / CVMFS)
asetup StatAnalysis,<VER>          # <VER> per the FastFrames changelog

# 2. Built install present? FastFrames is run via its script, not `command -v`:
ls <FF_DIR>/python/FastFrames.py   # the entry point
source <BUILD>/setup.sh            # puts the built libs + scripts in the env
```

If there is no built install, the user must clone + build (the
`documentation/installation/` page has the exact `cmake -S … -B build …` /
`cmake --build` / `cmake --install` / `source build/setup.sh` sequence). The
built **version** matters because the config schema is version-soft: confirm it
(the changelog / their checked-out tag) before quoting any block or key.

Because this setup is **tool-specific** (the StatAnalysis↔FastFrames version
pairing comes from the FastFrames changelog, not shared LCG infrastructure), it
lives here, not in `infra-advisor/reference/lcg-stacks.md`. Do **not** paste a
fixed `StatAnalysis,X.Y.Z` as if it were current — point at the changelog.

## Retrieval architecture (how this skill answers)

The docs are a **MkDocs** site registered in the `cerndocs` MCP as source
**`fastframes`**. Primary mechanism: the MCP. The page map (`reference/page-map.md`)
is the query-targeting index and the WebFetch fallback.

1. **`search_docs(query, source="fastframes")`** — BM25 hits (title/url/snippet).
   Map the question to a page: config blocks → `configuration/`; a run step →
   `histogramming/` or `ntupling/`; systematics → `systematics/`; batch →
   `distributed_computing/`; the fit hand-off → `trexfitter_integration/`;
   first-time setup → `tutorial/` + `documentation/installation/`.
2. **`fetch_doc(url, source="fastframes", mode="outline"|"sections:<h>"|"markdown")`**
   for the body. If `fetch_doc` cannot resolve the versioned `/latest/` path,
   **`WebFetch`** the public URL from `reference/page-map.md` instead (always works).
3. **Cite the public `…/latest/…` URL** so the user can open it.
4. If the MCP source is unavailable, fall back entirely to `WebFetch` over the
   baked page map; `WebSearch:
   site:atlas-project-topreconstruction.web.cern.ch/fastframesdocumentation
   <query>` if the page is unclear. The Doxygen site is the last resort for C++ internals.

Trust order if sources disagree: the user's **built FastFrames behaviour /
error output / generated config** > the `/latest/` docs > web. The docs are the
map; the installed version is the territory (it is version-soft).

## The config file at a glance (the #1 question)

FastFrames is steered by **one YAML config**. The top-level blocks (verify the
current set against `configuration/`):

| Block | What it holds |
|---|---|
| `general` | global settings & defaults (see below) — the most-edited block |
| `samples` | dataset definitions: DSIDs, MC campaigns, sample-level selections |
| `regions` | analysis regions: selections, variables, and the histograms to fill |
| `ntuples` | ntupling-mode output: `selection`, `branches`/`exclude_branches` (regex), `copy_trees` |
| `systematics` | systematic variations (and `automatic_systematics` in `general`) |
| `cutflows` | event-selection cutflow definitions |
| `truth_processing` | truth/particle-level processing (for unfolding etc.) |
| `numbering_sequence` | automated generation of repetitive variables/systematics |
| `simple_onnx_inference` | ONNX model integration (ML scores as columns) |
| `systematic_names_mapping` | harmonise systematic names across samples |

Key `general` keys (verify against `configuration/`):
`input_filelist_path` (the `filelist.txt` from the metadata step),
`output_path_histograms`, `output_path_ntuples`, `number_of_cpus`
(RDataFrame multithreading, default 1), `luminosity` (dict: MC campaign →
lumi), `xsection_files`, `default_event_weights`, `automatic_systematics`,
`nominal_only`, `custom_frame_name` (your custom C++ class), `debug_level`
(ERROR/WARNING/INFO/DEBUG/VERBOSE).

Always WebFetch `configuration/` and quote the exact keys — do not emit a key
from memory.

## Workflow — the commands (script-first)

```bash
# 1. Metadata: scan the input ROOT files → filelist + sum-of-weights.
python3 <FF_DIR>/python/produce_metadata_files.py \
  --root_files_folder <NTUPLE_DIR> --output_path metadata/
#    -> metadata/filelist.txt, metadata/sum_of_weights.txt
#       (point general.input_filelist_path at the filelist)

# 2. Run. --step h = histograms (default), --step n = ntuples.
python3 <FF_DIR>/python/FastFrames.py -c config.yml --step h
python3 <FF_DIR>/python/FastFrames.py -c config.yml --step n

# 3. Parallelise: pick samples, split a sample's files across jobs.
python3 <FF_DIR>/python/FastFrames.py -c config.yml --step h \
  --samples ttbar,wjets --split_n_jobs 20 --job_index 0

# 4. Batch submit (FastFrames' OWN wrapper — HTCondor or Slurm):
python3 <FF_DIR>/python/batch_submit.py --config batch_submit.yml
#    (for raw condor_q / held-job debugging, that's the `htcondor` skill)

# 5. Downstream: write a TRExFitter config (FastFrames does NOT run the fit):
python3 <FF_DIR>/python/produce_trexfitter_config.py \
  -c config.yml -o trex_config.config [--trex_settings extra.yml]
```

Placeholders: `<FF_DIR>` = the FastFrames source/install dir; `<NTUPLE_DIR>` =
the TopCPToolkit ntuple folder. Never invent a real path.

## Distributed running — three independent layers

- **`number_of_cpus`** (in `general`): RDataFrame **multithreading** on one node.
- **`--samples` / `--split_n_jobs` / `--job_index`**: split the work; *you* submit
  the pieces.
- **`batch_submit.py` + `batch_submit.yml`**: FastFrames' wrapper that submits the
  split jobs to **CERN HTCondor or a local Slurm**. The **grid** runner is
  `python/grid/run_ff_on_grid.py` (end-to-end on the grid, no intermediate
  ntuples staged).

Boundary: configuring `batch_submit.yml` / the split is **here**; generic
`condor_submit`/`condor_q`/held-job forensics is **`htcondor`**.

## TRExFitter integration (the downstream boundary)

`produce_trexfitter_config.py -c <ff_config> -o <trex_config>` auto-creates a
TRExFitter config from the FastFrames config; `--trex_settings <yml>` injects
things that cannot be derived (sample colours, region labels, norm factors,
extra systematics). FastFrames produces **(1) the TRExFitter config and (2) the
input histograms** — it does **not** run TRExFitter. Running the fit is the
user's separate step (no lumi TRExFitter skill yet; for open-data fitting,
`pyhf`).

## Honesty rules (specific to this skill)

- **Never quote a config block, key, default, or `StatAnalysis` version as the
  user's value.** The schema is version-soft — WebFetch `configuration/` /
  `changelog/` and quote with the source, or read it from the user's own config.
  Fabricating a key is a critical-rule-1 violation.
- **Respect the upstream/downstream boundary.** TopCPToolkit makes the input
  (`topcptoolkit`); TRExFitter runs the fit (FastFrames only writes its config +
  histograms). Do not drift into either from memory.
- **Sample-metadata is not config.** A DSID cross-section / sumOfWeights →
  `atlas-opendata`; FastFrames only *consumes* those numbers.
- **Do not hard-code the environment.** Setup is `setupATLAS` + `asetup
  StatAnalysis,<ver from changelog>` + a from-source build — never a pasted fixed
  version as if current.

## Output rules — what makes it into the user reply

- The `reference/page-map.md` file is **a loading instruction for you, not a
  citation for the user** (AGENTS.md output rules). Never quote its path; WebFetch
  and synthesise.
- Cite the **public `…/latest/…` URL** of the page you used.
- Emit valid, paste-ready **YAML** config blocks and exact command lines. Keep
  YAML indentation consistent (block or flow, not a broken mix).
- When you state a key or default, say where it came from (the `configuration/`
  page, or — preferred — the user's own config / changelog).
- Cite the skill name (`fastframes`) so the user can re-prompt.

## Version-bump procedure

The pin is the docs `/latest/` channel; the framework is version-soft.

1. The docs site auto-tracks `/latest/`. On a FastFrames release that changes the
   config schema or page set, **re-snapshot the page map**: GET
   `<base>sitemap.xml`, regenerate `reference/page-map.md`, and re-confirm the
   config-block list against `configuration/`.
2. Update the version-soft banner if the tutorial's pinned `vX.Y.Z` /
   `StatAnalysis,A.B.C` moved (these are illustrative, not authoritative — the
   changelog is).
3. Bump `VERSION` (patch for a page-map refresh; minor if coverage changes) and
   re-run `lint.py` + `run.py`.
