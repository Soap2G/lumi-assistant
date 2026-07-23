# CRIC ATLAS API — endpoint & field catalogue

Upstream: `https://atlas-cric.cern.ch/api/atlas/`. All examples are
public GET (no auth) unless flagged. Append `?json` (compact) or
`?json_pretty` (readable) to any `query/list/` path; filter with
`&<field>=<value>`.

Responses are a JSON **object keyed by the entity name**, not an array
— iterate `.items()`.

---

## `site/query/list/` — grid sites

The site is the top grouping: it owns DDM endpoints and PanDA queues.

Useful fields (string/int ones also work as `&field=value` filters;
boolean fields like `is_pledged` are **not** filterable — see the recap
at the bottom):

| Field | Meaning |
|---|---|
| `name` | Site name (CRIC key), e.g. `AGLT2`, `CERN-PROD`, `BNL-ATLAS` |
| `tier_level` | WLCG tier: `0`, `1`, `2`, `3` |
| `cloud` | ATLAS cloud, e.g. `US`, `DE`, `CERN`, `UK` |
| `country` / `country_code` | Host country |
| `state` | Config state, e.g. `ACTIVE` |
| `status` | Operational status |
| `vo_name` | VO, `atlas` |
| `rc_site` | Resource-Center (GOCDB/OIM) site name |
| `is_pledged` | Whether resources are WLCG-pledged |
| `ddmendpoints` | The DDM endpoints hosted here |
| `grid_flavour` | Middleware flavour |
| `latitude` / `longitude` / `timezone` | Geo |

```bash
# All Tier-1s:
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json&tier_level=1'
# Everything in the US cloud:
curl -s 'https://atlas-cric.cern.ch/api/atlas/site/query/list/?json&cloud=US'
```

---

## `ddmendpoint/query/list/` — DDM storage endpoints (= Rucio RSEs)

A DDM endpoint is the CRIC record for a **Rucio RSE**. This is the
bridge to the `rucio` skill: the endpoint `name` is (normally) the RSE
name, and `token` is its space token.

| Field | Meaning |
|---|---|
| `name` | Endpoint / RSE name, e.g. `AGLT2-S3_LOCALGROUPDISK` |
| `token` | Space token, e.g. `ATLASLOCALGROUPDISK`, `ATLASDATADISK` |
| `type` | Endpoint type: `LOCALGROUPDISK`, `DATADISK`, `SCRATCHDISK`, `DATATAPE`, … |
| `is_tape` | Tape vs disk (`True`/`False`) |
| `is_cache` | Whether it's a cache endpoint |
| `se_flavour` | Storage-element flavour, e.g. `DPM`, `dCache`, `EOS`, `StoRM`, `XROOTD` |
| `state` | `ACTIVE` / `DISABLED` (DISABLED ≈ blacklisted) |
| `status` | Operational status |
| `endpoint` | Base path/URL of the SE area |
| `aprotocols` / `rprotocols` / `arprotocols` | Access / read / access-read protocol lists (WebDAV, XRootD, SRM, gsiftp…) |
| `quotas` | Configured quotas |
| `space_method` / `space_usage_url` | How free/used space is reported |
| `rc_site` | Owning Resource-Center site |
| `tier_level` | Tier of the owning site |
| `phys_groups` | Physics groups with space here (for `*GROUPDISK`) |

```bash
# All tape endpoints — filter the string `type`; the boolean is_tape is NOT filterable:
curl -s 'https://atlas-cric.cern.ch/api/atlas/ddmendpoint/query/list/?json&type=DATATAPE'
# Every endpoint at one site:
curl -s 'https://atlas-cric.cern.ch/api/atlas/ddmendpoint/query/list/?json&rc_site=BNL-ATLAS'
# All DATADISK endpoints:
curl -s 'https://atlas-cric.cern.ch/api/atlas/ddmendpoint/query/list/?json&type=DATADISK'
```

Hand-off to `rucio`: once you have the RSE `name` here, `rucio` answers
what *data* is on it (`rucio replica list …`, `rucio rule list …`).
CRIC = the endpoint's config; Rucio = the endpoint's contents.

---

## `pandaqueue/query/list/` — PanDA compute queues

A PanDA queue is a compute resource fed by Harvester/pilots. Keyed by
queue `nickname`.

| Field | Meaning |
|---|---|
| `nickname` / `name` | Queue name, e.g. `AGLT2_UCORE`, `CERN-PROD_UCORE` |
| `panda_resource` | PanDA resource name |
| `atlas_site` / `panda_site` | Owning ATLAS / PanDA site |
| `resource_type` | `GRID`, `HPC`, `CLOUD`, … |
| `status` | `online` / `offline` / `brokeroff` / `test` |
| `state` | Config state, e.g. `ACTIVE` |
| `queues` | The CEs behind it (e.g. `HTCONDOR-CE`, `ARC-CE`) + their state |
| `corecount` | Cores per job slot (1 = single-core, >1 = multicore/UCORE) |
| `maxtime` | Max walltime (s) |
| `maxrss` / `maxinputsize` / `maxwdir` | Memory / input / workdir limits |
| `releases` / `validatedreleases` | Cached / validated software releases |
| `is_cvmfs` | CVMFS available |
| `cloud` | ATLAS cloud |
| `tier` | Tier / T2D flag |
| `vo_name` | `atlas` |
| `harvester` / `pilot_manager` / `pilot_version` | Pilot plumbing |
| `catchall` / `params` / `environ` / `uconfig` | Advanced free-form config |

```bash
# One site's queues:
curl -s 'https://atlas-cric.cern.ch/api/atlas/pandaqueue/query/list/?json&rc_site=CERN-PROD'
# Only online queues in the US cloud:
curl -s 'https://atlas-cric.cern.ch/api/atlas/pandaqueue/query/list/?json&cloud=US&status=online'
```

`status` here is the **configured** operational status. The live
per-probe status (from ATLAS site-availability probes) lives in the
gated `pandaqueuestatus` feed below.

---

## `vofeed/list/` — WLCG VO-feed (XML)

`https://atlas-cric.cern.ch/api/atlas/vofeed/list/` returns the WLCG
VO-feed **XML** (not JSON): the topology export that SAM/ETF and other
WLCG monitoring consume. Use it when the user explicitly wants the VO
feed / monitoring topology; for normal lookups the JSON objects above
are easier.

---

## Auth-gated feeds (403 anonymously — do not call from this skill blindly)

These need a CERN identity (grid cert / SSO) **and** a `view_*`
permission; anonymous GET returns HTTP 403. Their field schema can only
be inspected once authenticated — don't guess it.

| Path | What it gives |
|---|---|
| `ddmendpointstatus/query/list/` | Current per-probe status of DDM endpoints |
| `ddmendpointstatus/query/history/` | DDM endpoint status time series |
| `pandaqueuestatus/query/list/` | Current per-probe PanDA queue status |
| `pandaqueuestatus/query/history/` | PanDA queue status time series |
| `*/update/…` | **Write** ops (set state/attributes/probe status) — never call |

If the user needs a live probe status, state that it is auth-gated and
point them at the CRIC web UI or their authenticated client. Never
substitute a configured `status`/`state` value for a live probe value
without saying which one it is.

---

## Query mechanics recap

- Output: `?json` (compact) or `?json_pretty` (indented). HTML/XML/text
  are also offered on some paths; JSON is the one to script against.
- Filter: `&<field>=<value>` on **string/int** fields (`type`,
  `tier_level`, `rc_site`, `cloud`, `status`), ANDed across multiple
  fields (`&cloud=US&status=online`). **Boolean fields are NOT
  filterable** — `&is_tape=True` (or `true`) returns HTTP 400; filter an
  equivalent string field (`type=DATATAPE`) or filter client-side.
- Responses are objects keyed by entity name — `.items()`, not `[i]`.
- Always filter before fetching; unfiltered `query/list` is hundreds of
  entries.
