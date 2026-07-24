---
name: cric
description: Use when the user needs ATLAS / WLCG computing-resource topology or operational state from CRIC (Computing Resource Information Catalog, atlas-cric.cern.ch): which grid sites exist (tier/cloud/country), the DDM storage endpoints (Rucio RSEs) at a site (protocols, space-token, tape-vs-disk, ACTIVE/DISABLED state), or the PanDA compute queues (CE type, corecount, max-walltime, cached releases, online/offline). Read topology is public JSON — GET `<object>/query/list/?json` for `site`/`ddmendpoint`/`pandaqueue`, filter `&<field>=<value>` (e.g. `&tier_level=0`). Covers BOTH the static catalog AND live WLCG operations (queue online/offline, endpoint blacklisting); per-probe `*status`/`history` feeds are auth-gated. NOT Rucio DID/replica/rule queries (use `rucio`: CRIC describes the RSEs Rucio moves data into), NOT submitting/monitoring PanDA or HTCondor jobs (use `htcondor`), NOT prose how-tos (use `cern-docs`), NOT multi-service picks (use `infra-advisor`). Disambiguator phrase: CRIC WLCG topology catalog.
data_scope: both
experiment: all
---

# cric — ATLAS / WLCG computing-resource topology & operational state

Upstream service: **https://atlas-cric.cern.ch** (API root:
`https://atlas-cric.cern.ch/api/atlas/`).
Docs (public): https://atlas-cric.docs.cern.ch — also full-text
searchable through the `cern-docs` skill (`cerndocs` MCP, source
`atlas-cric`) for CRIC concepts, the object model, and how-to guides.

CRIC — the **Computing Resource Information Catalog** — is the
authoritative topology system for ATLAS distributed computing: the
single source of truth for *which sites, storage endpoints, and compute
queues exist, how they are configured, and what operational state they
are in*. PanDA, Rucio, and the monitoring stack all read their topology
from it.

## This skill is reference AND operations

Treat CRIC as two things at once — say which one you are answering:

- **Reference (the static catalog).** "What tier is DESY-HH?", "Which
  space token does the AGLT2 LOCALGROUPDISK endpoint use?", "What CE
  flavour and max walltime does the CERN-PROD analysis queue have?".
  These are answered from the public `query/list` topology and never
  change per-second.
- **WLCG operations (the live control plane).** CRIC is also where a
  site's queues are set online/offline, where a storage endpoint is
  marked ACTIVE / DISABLED (blacklisted), and where downtimes and probe
  history are recorded. The *configured* state (`state`, `status`
  fields) rides on the public topology; the *per-probe time series*
  (`ddmendpointstatus`, `pandaqueuestatus`, `.../query/history/`) is
  **auth-gated** — see "Auth boundary" below.

## When to load this skill

- "List the ATLAS Tier-1 sites / all US-cloud sites."
- "What are the DDM storage endpoints at BNL-ATLAS, and which are tape?"
- "Show the PanDA queues for CERN-PROD and whether they're online."
- "What's the space token / protocol for `<RSE>`?"
- "Which sites have a LOCALGROUPDISK?"
- "Is `<queue>` online right now?" (configured state — public;
  live probe status — needs auth.)

Do NOT load this skill for:

- **Rucio data-catalog queries** — DIDs, replicas, rules, `rucio
  whoami` → use `rucio`. CRIC tells you what an RSE *is* (protocols,
  token, tier, tape/disk); Rucio tells you what *files* are on it.
- **Running jobs** — `condor_submit`, PanDA task submission,
  monitoring a *running* job → use `htcondor` (CRIC only describes the
  queues, it does not submit to them).
- **Prose "how does service X work"** → use `cern-docs`.
- **"What stack should I use end-to-end"** → use `infra-advisor`.

## The public read API

Topology reads need **no authentication** — plain HTTP GET.

```bash
# Compact JSON (machine-readable):
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json'
# Human-readable JSON:
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json_pretty'
```

Three topology objects, each at `<object>/query/list/`:

| Object | What it is | Neighbour concept |
|---|---|---|
| `site` | A grid site: tier, cloud, country, the RSEs it hosts | the "Resource Center" grouping |
| `ddmendpoint` | A DDM storage endpoint = a **Rucio RSE**: protocols, space token, tape/disk, state | `rucio` RSE |
| `pandaqueue` | A **PanDA** compute queue: CE flavour, corecount, walltime, cached releases, online/offline | `htcondor` CE / batch |

Plus `vofeed/list/` — the WLCG **VO-feed** (XML), the topology export
consumed by SAM/ETF monitoring. It is a feed, not a `query/list`.

### Filtering — always narrow before you fetch

The `query/list` responses are **large** (hundreds of sites/queues).
Filter server-side by appending `&<field>=<value>` — **string and
integer** fields work (confirmed: `tier_level`, `type`, `rc_site`):

```bash
# Just the Tier-0 (returns CERN-PROD, CERN-T0):
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json&tier_level=0'
# Tape endpoints only — filter the string `type`, NOT the boolean is_tape:
curl -s 'https://atlas-cric.cern.ch/api/atlas/ddmendpoint/query/list/?json&type=DATATAPE'
# One site's PanDA queues:
curl -s 'https://atlas-cric.cern.ch/api/atlas/pandaqueue/query/list/?json&rc_site=CERN-PROD'
```

**Boolean fields are not filterable** — `&is_tape=True` (or `true`)
returns **HTTP 400**. To narrow by a boolean property, filter on an
equivalent string field (e.g. `type=DATATAPE` for tape) or fetch and
filter the boolean client-side. If you need only a couple
of fields, still fetch filtered and pick the keys client-side (the API
returns the full object per entry).

### Project fields — never dump the whole list into context

Each object carries its full nested config, so an unfiltered
`site/query/list/?json` is **~14,000 lines**. Do NOT fetch that whole
blob into context and `grep` it: `grep` can't tie a nested value back to
its site (the top-level key and the nested `rcsite.name` often differ,
e.g. `ARC-TEST` → `NDGF-T1`), and tool output truncates.

**Project** to the fields you need with `curl … | jq` (both are
permission-allowlisted for the CRIC host — no prompt):

```bash
# One short line per site — name, country, tier, state (~600 lines, not 14k):
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json' \
  | jq -r 'to_entries[] | [.key, .value.country_code, .value.tier_level, .value.state] | @tsv'
```

then filter client-side. Same shape for `ddmendpoint`
(`.value.token, .value.type, .value.is_tape`) and `pandaqueue`
(`.value.status, .value.resource_type, .value.corecount`). Prefer this
over the `webfetch` tool — it returns the whole body and cannot project
(and only accepts `text|markdown|html`, so a `?json` URL must be fetched
as `text`). No `jq` available? Hand the saved JSON to a subagent to
parse; never grep it inline.

### Geography and other non-field filters

There is **no continent field and no free-text search** — a server-side
filter is exact-match on one string/int field. Geographic questions
("sites in Europe") are answered client-side by projecting `country_code`
(ISO-2) and filtering. Sanity-check the result, don't assert a hard count:

- `country_code` is sysadmin-declared; some entries are cloud / volunteer
  / test with off-geography codes (`BOINC`, `GOOGLE`, `*_TEST`, and US
  institutes such as `KIPAC` / `NOSAMS`).
- RU / TR / AM / GE straddle Europe/Asia — state the cut you used and flag
  the ambiguous entries rather than presenting a single definitive number.

The exhaustive per-object field catalogue (what each key means, the
useful filters, and copy-paste examples) is in
[reference/endpoints.md](reference/endpoints.md) — read it before
constructing a non-obvious query.

## Auth boundary — what needs CERN credentials

| Path | Anonymous? |
|---|---|
| `site` / `ddmendpoint` / `pandaqueue` `→ query/list/` | ✅ public GET |
| `*status` / `*` `→ query/list/` and `query/history/` (live probe time series) | ❌ 403 — needs CERN auth + `view_*` permission |
| any `update/…` (set state, attributes, probe status) | ❌ auth + write permission; **never call from this skill** |

For the gated read feeds the user needs a CERN identity (grid
certificate / SSO); this skill stays on the public topology. If a live
per-probe status is genuinely required, say so and point the user at
the CRIC web UI or their authenticated client — do not fabricate a
status.

## Querying from Python

```python
import httpx
base = "https://atlas-cric.cern.ch/api/atlas"
r = httpx.get(f"{base}/pandaqueue/query/list/",
              params={"json": "", "rc_site": "CERN-PROD"}, timeout=30)
r.raise_for_status()
queues = r.json()          # dict keyed by queue name
online = [q for q, v in queues.items() if v["status"] == "online"]
```

The response is a JSON **object keyed by the entity name** (site name,
endpoint name, queue nickname), not a list — iterate `.items()`.

## Never fabricate topology

Site lists, RSE tokens, queue states, tier assignments — every one of
these must come from an actual CRIC call in this session. If the call
fails (network, 403 on a gated feed), report the failure; do not fall
back to a "typical" ATLAS site list from memory. This is critical rules
1, 2 and 6 (see AGENTS.md) applied to computing topology.

## Output rules

- Cite the **public CRIC URL** the user can open — the web view
  (`https://atlas-cric.cern.ch/atlas/pandaqueue/list/`) or the API URL
  you actually queried. Never cite `reference/endpoints.md` or any
  in-bundle path.
- When you report a state, say whether it is the **configured** state
  (from public topology) or a **live probe** state (gated) — they can
  differ, and conflating them misleads operators.
- Name the neighbour skill when redirecting: `rucio` for what's *on* an
  RSE, `htcondor` for *submitting* to a queue, `cern-docs` for prose.

## Verification

A successful use ends with either a concrete topology answer grounded
in a shown CRIC query (site/endpoint/queue named, with the field that
answered the question), or an explicit statement that the needed feed
is auth-gated and was not reachable anonymously.

If the query implies **all** of something ("all sites in X", "every tape
endpoint"), the answer must be the **complete** set — a capped grep (100
matches), a truncated tool slice, or a "first ~30" list is a truncation,
not the answer. Project with `jq` and **count** before claiming
completeness.
