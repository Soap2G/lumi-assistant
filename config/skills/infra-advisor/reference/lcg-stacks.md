# LCG views — environment setup & stack pins (single source of truth)

This file is the ONE place to bump when the CERN LCG software stack changes.
Tool skills (`sherpa-manual`, and future LCG-provided tools) deliberately carry
NO stack version — they probe the binary (see **Detecting a tool** below) and
defer here for setup. AGENTS.md "## Environment" describes the mechanism
generically and points at this file for the current values.

## Mechanism

LCG "views" are pre-built software stacks on CVMFS. Source one to put its tools
(event generators, ROOT, Python, analysis libraries, …) on PATH:

```bash
source /cvmfs/sft.cern.ch/lcg/views/<STACK>/<PLATFORM>/setup.sh
```

- `<STACK>` — the LCG release, e.g. `LCG_107`.
- `<PLATFORM>` — `<arch>-<os>-<compiler>-<build>`, e.g. `x86_64-el9-gcc13-opt`.
  Match the host OS (`el9`, `el8`, …) and compiler; `-opt` is optimised,
  `-dbg` is debug.

Requires the CVMFS mount `/cvmfs/sft.cern.ch` (present on lxplus, SWAN, many
CERN nodes; mountable elsewhere via cvmfs). Detect the mount with
`ls /cvmfs/sft.cern.ch` before assuming a view can be sourced.

> **Shell state does not persist between commands.** Each Bash tool call runs in
> a fresh shell, so a `source …/setup.sh` in one call is gone by the next. Always
> **source the view and run the tool in a single chained command**:
> ```bash
> source …/setup.sh && export … && <tool> …
> ```
> Sourcing in one call and running in another will fail with missing libraries.

## Detecting a tool — presence is not runnability

`command -v <tool>` returning a path means the binary is on PATH. It does **not**
mean the tool will run: the view can leave the binary reachable while its shared
libraries are not on `LD_LIBRARY_PATH` (see **Runtime quirks** below). Always use
a **functional probe** — source the view, then ask the tool for its version, in
one command:

```bash
source /cvmfs/sft.cern.ch/lcg/views/<STACK>/<PLATFORM>/setup.sh && <tool> --version
```

A clean exit **and** a printed version banner means it is genuinely runnable. An
`error while loading shared libraries: …` means a runtime quirk applies — fix the
environment per the table below, do not report the tool as unavailable.

## Runtime quirks (per tool)

Some tools need environment beyond what `setup.sh` provides. Apply the fix, then
re-run the functional probe. Derive paths from the tool's own `*-config` helper
where possible so the fix survives a stack bump without hard-coding `LCG_<NNN>`.

| Tool | Symptom | Fix (after sourcing the view) |
|---|---|---|
| Sherpa | `error while loading shared libraries: libSherpa*.so` — `setup.sh` omits Sherpa's own lib dir from `LD_LIBRARY_PATH` | `export LD_LIBRARY_PATH="$(Sherpa-config --prefix)/lib64/SHERPA-MC:$LD_LIBRARY_PATH"` |

*(`Sherpa-config --prefix` resolves to the release dir whose `lib64/SHERPA-MC/`
holds `libSherpaMain.so` etc.; verified runnable on LCG_107. Extend this table as
other LCG tools reveal runtime quirks.)*

## Current pin

| Field | Value |
|---|---|
| LCG stack | **LCG_107** |
| Default platform | **x86_64-el9-gcc13-opt** |
| Setup line | `source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh` |

### Tool versions provided by this stack

| Tool | Version in LCG_107 | Pinned docs / skill |
|---|---|---|
| Sherpa | **3.0.1p2** | manual v3.0.1 → `sherpa-manual` |
| MadGraph5_aMC@NLO | **3.5.7** | corpus-soft → `madgraph` |

*(Extend this table as more LCG-provided tools get skills.)*

## When you bump the stack

1. Update the **Current pin** table (stack number; platform if the OS/compiler
   moved) and the setup line.
2. Update the **Tool versions** table for every tool whose version changed.
3. For any tool whose version crossed a **docs boundary** (e.g. Sherpa
   3.0.1p2 → 3.0.5, where the manual moves v3.0.1 → v3.0.5), run that skill's
   own **Version-bump procedure** (for `sherpa-manual`: re-pin the URLs and
   re-snapshot `reference/page-map.md`). Editing THIS file does **not**
   auto-update a skill's baked page map — that is a separate, deliberate step.
