# LLM Execution Guide — avoiding known mistakes in this repo

> For LLM agents (Opus / Sonnet / Fable-class) executing a version brief,
> authoring a skill, or refactoring anything under `config/`. Companion to
> `docs/skill-design.md` (the architectural WHY) — this file is the
> operational HOW-NOT-TO-FAIL, distilled from a full repo review
> (2026-06-10, at v1.15.0) of real drift found in the tree.

## 0. Trust the tree, not the brief

Execution briefs (`docs/*-execution-brief.md`, vault notes like
`lumi-sherpa-skill-plan.md`) describe an **intended** future. The tree is the
only ground truth. Proof this matters: `docs/v1.10-v1.12-execution-brief.md`
promised `health.py`, `propagation.yaml`, and `INDEX.md` — none exist. The
actual v1.10–v1.12 commits did entirely different things (fts-rest, the
experiment axis, vendor generalisation). An agent that "resumes" that brief
would be executing a plan the maintainer abandoned.

Before any edit:

```bash
cat VERSION                      # never hard-code the bump target; compute current+1
git log --oneline | head -10     # what actually happened recently
git status --short               # know what is untracked/dirty before you add to it
python config/evals/lint.py     # baseline must be green BEFORE you start
```

If a brief quotes "the file currently reads X" — **diff X against the actual
file before editing**. Enumerations drift (see §4). If the quoted anchor text
is absent or different, reconcile and say so in the commit message; do not
blind-insert.

## 1. Invariants — violating any of these is a review failure

1. **Descriptions are the router interface** (Principle 0). Every
   `description:` carries: trigger condition, NOT-covered list naming each
   neighbor skill, one greppable disambiguator phrase unique in the library.
   Grep the disambiguator across `config/` before committing.
2. **Intent bucket first, source-named skill second.** Category = what the
   user is trying to do (`reference/`, `access/`, …); skill name = the source
   or tool (`cern-docs`, `pdg-lookup`, `sherpa-manual`). Never name a skill
   after a bare ambiguous token that collides with sample names (`sherpa`
   collides with `Sh_…` physics_shorts; use `sherpa-manual`).
3. **Every skill has `data_scope: open|internal|both` and
   `experiment: atlas|cms|lhcb|alice|all`.** lint.py enforces presence;
   YOU are responsible for the values being true.
4. **Vendored skills are build artifacts.** If the file header says
   "Vendored from … do not edit", edit
   `script/vendor/<skill>.frontmatter.md` and re-run
   `python script/sync_vendored.py`. A direct edit will be silently
   reverted on the next sync and fails CI (`sync_vendored.py --check`).
5. **Environment pins live in exactly one file.** No `LCG_<NNN>`, CVMFS
   stack path, or tool version baked into a tool skill — detection is
   `command -v <tool>`, setup defers to the central reference
   (`infra-advisor/reference/lcg-stacks.md` once it lands). Same discipline
   as docs-version pinning: one bumpable constant per variable.
6. **Docs-backed skills pin the manual version of the binary users run**,
   not the newest manual (Sherpa: LCG ships 3.0.1p2 → cite the v3.0.1
   manual, not v3.0.4). Every cited URL carries the pinned version. Ship a
   version-bump procedure in the skill body.
7. **No `Co-Authored-By:` lines in commits.** One commit per version;
   commit message style follows existing `git log` (vN.N.N prefix, body
   explains architecture, ends with `VERSION: old -> new`).
8. **Bump `VERSION`** in the same commit, and keep `README.md` +
   `config/AGENTS.md` enumerations in sync (§4).

## 2. The eval harness's real semantics (the #1 trap)

`config/evals/run.py` scores **every** prompt under `should_not_match` as a
pass only if the router answers literally `NONE`. There is no mechanism to
express "must not route to skill X but routing to Y is fine".

The library has already tripped on this: `cases.yaml` contains "cliff guard"
entries whose own comments say they should route to a real skill —
"Get me the cross-section for ttbar from PDG" (→ `pdg-lookup`),
"What do the official CERN batch documentation pages say about HTCondor
authentication?" (→ `cern-docs`, and a near-identical prompt sits in
`cern-docs`' *should_match*), "How do I submit an HTCondor job to lxbatch
at CERN?" (→ `htcondor`). A correct router FAILS these. Consequences:

- **Do not assume a green baseline.** Run the harness first and record the
  pass count; judge your change by the delta, not by absolute green.
- **A cliff guard whose correct answer is another skill belongs under that
  skill's `should_match`**, not under `should_not_match` — that already
  asserts "not your new skill" because the harness checks top-1 equality.
- Reserve `should_not_match` for prompts where abstention really is right
  (off-topic, scope-mismatch with no in-library answer).
- Acceptance criteria of the form "guard must route to `atlas-opendata`"
  (e.g. sherpa brief §5.2/§6) are unverifiable by `should_not_match` as
  implemented. Either place the prompt in `should_match: atlas-opendata`
  or extend the schema first — and say which you did in the commit.
- Never "fix" a failing guard by weakening a *neighbor's* description.
  Sharpen the new skill's NOT-covered list instead.

## 3. Three files must agree (and currently don't)

Skill lists are enumerated in three places that drift independently:
`config/skills/**` (truth), `config/AGENTS.md` "Library structure", and the
`README.md` layout tree. Observed drift at v1.15.0 — do not propagate it:

- AGENTS.md omits `fts-rest`, `hepdata`, `read-publication`, `htcondor`,
  `cds-search`, `pdg-lookup` from its bucket enumeration, and still says the
  cerndocs MCP indexes "seven MkDocs-based" sites — it is **eight**, and
  `fts` is GitBook, with `fetch_doc` available (the `cern-docs` SKILL.md is
  the corrected, authoritative wording).
- README's layout tree omits `hepdata`, `read-publication`, `fts-rest`,
  `pdg-lookup`.
- AGENTS.md says the design guide "lives outside this repo" —
  `docs/skill-design.md` is in-repo and declares itself authoritative.

When your change touches the skill set, fix the **whole stale line** you're
editing (you'll usually find the entries that should already be there,
aren't), and prefer pointing AGENTS.md at the in-repo guide.

## 4. Configuration traps (`config/opencode.json`)

- The `cds` MCP entry is `"type": "local"` with a hard-coded
  `/Users/gguerrie/...` path. It works on exactly one laptop. Anything you
  add to `mcp:` must be remote or resolvable on lxplus/SWAN/CVMFS; treat
  this entry as a known defect, not a pattern to copy.
- `"small_model": "litellm/mistral-small-latest"` references a model not
  declared under the `litellm` provider's `models`. Declare what you
  reference.
- The permission map is deny-by-default-ish (`"*": "ask"`) with explicit
  read-only allows and destructive denies (`rucio * remove`,
  `reana-client delete`, `fts-rest-ban`, `rm`). New tool skills must come
  with matching permission entries in the same spirit: read-only → allow,
  write → ask, destructive → deny.
- `dist/` is gitignored but a stale `dist/cvmfs-stage/0.1.0/` tree (old flat
  skill layout, old opencode.json) may exist on disk. `cvmfs-deploy.sh`
  publishes the **entire** stage tree — clean or restage before any publish.

## 5. Content rules your skill bodies must obey

These bind the runtime assistant, so authored bodies must never contradict
them (AGENTS.md "Critical rules" is the source):

- **No physics numbers from memory.** Cross-sections, BRs, k-factors,
  sumOfWeights, PDG constants come from a tool call or a cited record.
  In examples, never invent a DSID↔physics_short pairing — check it. (The
  quick-reference's juxtaposed examples, DSID `301204` and
  `Sh_2211_Zee_maxHTpTV2_BFilter`, are **different samples** — 301204 is
  `Pythia8EvtGen_…_Zprime_NoInt_ee_SSM3000` in 2024r-pp. Verified via
  `atlas_get_metadata` 2026-06-10.)
- **MC weight formula, always explicit and identical everywhere:**
  `weight = cross_section_pb * 1000 * kFactor * genFiltEff * mcWeight / sumOfWeights * luminosity_fb`.
- **Rucio: noun-verb only** (`rucio did list`, `rucio rule add`). Any flat
  verb (`list-dids`, `add-rule`, `get-metadata`) in a body or example is a
  bug.
- **Sherpa v3 = YAML `Sherpa.yaml`.** Never emit v2 `Run.dat`
  `(run){…}(end)` syntax; training-data memory of Sherpa is mostly v2.
- **PHYSLITE is MeV**; convert before plotting. `mcEventWeights[0]` is the
  nominal weight.
- **PDFs:** opencode's `Read` returns raw bytes; bodies must instruct
  `pdftotext` → `pypdf` fallback, never "paste the text back to me". Note
  `pdg-lookup`'s "cheapest surface" table labels listing pages "HTML" but
  links `.pdf` files — every such lookup goes down the PDF-extraction path;
  prefer pdgLive HTML pages where they exist.
- **Internal paths never reach the user reply.** Cite skill names and
  canonical public URLs; `reference/*.md` paths are loading instructions,
  not citations.
- **Capability claims require demonstration** (critical rule 6): bodies
  should phrase fallbacks as "run, observe, report the actual error".

## 6. Pre-commit checklist (run it, don't recall it)

```bash
python config/evals/lint.py              # structural — must be green
python script/sync_vendored.py --check   # vendored drift — must be green
python config/evals/run.py               # routing — compare against the
                                         # PRE-CHANGE pass count (§2);
                                         # zero regressions on neighbors
grep -rn "<your disambiguator>" config/  # appears exactly once
```

Plus by hand: VERSION bumped; README tree + AGENTS.md enumerations updated
(all three, §3); new skill has 3–5 `should_match` prompts; redirects in your
NOT-covered list point at skills that exist; no upstream URL cited without
its version pin; no local-filesystem path anywhere in `config/`.

## 7. If something fails

Stop, report the actual command output, and do not commit. "Should have
worked" is not evidence — the repo ships a whole skill
(`verification-before-completion`) saying exactly this. It applies to you,
the executing agent, just as much as to the runtime assistant.
