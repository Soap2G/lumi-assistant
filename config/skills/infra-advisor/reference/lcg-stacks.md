# LCG views — environment setup & stack pins (single source of truth)

This file is the ONE place to bump when the CERN LCG software stack changes.
Tool skills (`sherpa-manual`, and future LCG-provided tools) deliberately carry
NO stack version — they detect the binary with `command -v <tool>` and defer
here for setup. AGENTS.md "## Environment" describes the mechanism generically
and points at this file for the current values.

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
