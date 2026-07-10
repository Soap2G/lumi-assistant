---
name: rucio
description: Use when the user needs authenticated Rucio data-management queries — DIDs, RSEs, replicas, metadata, replication rules — on collaboration-internal data, via EITHER the remote `rucio-*` MCP tools (rucio-atlas, rucio-cms, rucio-escape, rucio-fcc; per-user SSO, no local client needed) OR the Rucio v38+ CLI on lxplus, SWAN, or a CVMFS-staged client (`/cvmfs/sw.escape.eu/rucio/<version>/`). Read queries default to the MCP tools; `rucio download`/`upload` and rule writes require the CLI. CLI is ALWAYS noun-verb (`rucio rse list`, `rucio did show`, `rucio rule add`); NEVER the deprecated flat verbs (`list-rses`, `list-dids`, `add-rule`, `get-metadata`, `rule-info`) even though MCP tool names (`rucio_list_dids`) resemble them. Targets non-public datasets — for ATLAS Open Data DSIDs use `atlas-opendata` instead; for grid submission use PanDA, not Rucio directly. Disambiguator phrase: rucio v38 noun-verb.
data_scope: internal
experiment: all
---

## Transport selection: MCP tools vs CLI

Rucio is reachable over two transports. Pick per flow, not per session:

| Flow | Transport | Why |
|---|---|---|
| DID discovery, metadata, replica location, rule *inspection*, RSE/account/quota queries | **MCP tools** (`rucio-atlas_*`, `rucio-cms_*`, `rucio-escape_*`, `rucio-fcc_*`) | Per-user SSO token, no `rucio.cfg`/VOMS/CLI needed, works off-lxplus |
| `rucio download` / `rucio upload` (moving bytes to/from the user's disk) | **CLI only** | The MCP server has no download/upload tools — it cannot move bytes to the user's machine |
| Rule writes (`rule add/move/update/remove`) | **CLI only, with explicit user confirmation** | The MCP rule-write tools are disabled in this config; the CLI path is permission-gated (ask/deny) |
| Scripting / loops over many DIDs the user will re-run | **CLI** | Reproducible outside the assistant |

Pick the MCP server matching the user's VO: `rucio-atlas` for ATLAS,
`rucio-cms` for CMS, `rucio-escape` for the ESCAPE datalake,
`rucio-fcc` for FCC. On first use the user is sent through a browser
SSO login; the resulting token is their own Rucio identity
(`rucio-atlas_rucio_whoami` confirms the mapped account).

**No local browser (lxplus / SSH session)?** The default OAuth flow
dead-ends: it redirects the browser to `http://127.0.0.1:19876/...`,
which only works when browser and opencode share a machine. Use the
shipped helper instead — run `lumi-rucio-auth <server>` (on PATH after
`source setup.sh`), open the printed URL in a browser on any device,
log in, then paste back the full `http://127.0.0.1:19876/...` URL the
browser fails to load. The helper exchanges the code locally and the
MCP tools work immediately. Tokens are Rucio session tokens (~1 h);
re-run the helper when one expires. You can drive this for the user:
`lumi-rucio-auth <server> --start` prints the URL, then
`lumi-rucio-auth <server> --finish '<pasted URL>'` completes it. If
even that is not possible, fall back to the CLI path below.

**Naming firewall**: MCP tool names (`rucio_list_dids`,
`rucio_get_metadata`) deliberately mirror Rucio's *deprecated* flat-verb
CLI. Never let them leak into a shell command — anything you type after
`rucio ` in Bash must be noun-verb.

## CRITICAL: emit only v38+ noun-verb commands

Rucio 36+ deprecated the flat-verb CLI. The flat forms still print a
`WARNING: This method is being deprecated` and will be removed. **Never
emit them.** Always use the noun-verb form:

| ❌ Do NOT emit (deprecated) | ✅ Use instead |
|---|---|
| `rucio list-rses` | `rucio rse list` |
| `rucio list-dids '<scope>:<pattern>'` | `rucio did list '<scope>:<pattern>'` |
| `rucio list-files <did>` | `rucio did content list <did>` |
| `rucio list-content <did>` | `rucio did content list <did>` |
| `rucio list-parent-dids <did>` / `rucio stat <did>` | `rucio did show <did>` |
| `rucio get-metadata <did>` | `rucio did metadata list <did>` |
| `rucio list-file-replicas <did>` | `rucio replica list file <did>` |
| `rucio list-dataset-replicas <did>` | `rucio replica list dataset <did>` |
| `rucio list-rules <did>` | `rucio rule list <did>` |
| `rucio rule-info <rule_id>` | `rucio rule show <rule_id>` |
| `rucio add-rule <did> <n> <rse>` | `rucio rule add <did> <n> <rse>` |
| `rucio delete-rule <rule_id>` | `rucio rule remove <rule_id>` |
| `rucio list-account-limits <a>` / `rucio list-account-usage <a>` | `rucio account limit list <a>` |
| `rucio list-rse-attributes <rse>` | `rucio rse attribute list <rse>` |

If you ever see yourself about to type `rucio <verb>-<noun>`, stop and
rewrite it as `rucio <noun> <verb>`. The full catalogue lives in
[reference/commands.md](reference/commands.md).

## Scope

Use this skill when the user is working with real experiment data
(not ATLAS Open Data files). The MCP transport has no local
prerequisites beyond completing the browser SSO login. The CLI
transport additionally requires:

- the `rucio` command on their PATH, **and**
- a working `rucio.cfg` plus the credential that matches its
  `auth_type` (VOMS proxy for `x509_proxy`, cached OIDC token for
  `oidc`, etc.).

For public ATLAS Open Data release samples, use `atlas-opendata`
(`atlas_get_urls`) or `cern-opendata` (`cod_list_files`) instead.

Do **not** invoke write operations (`rucio rule add`, `rucio did add`,
`rucio upload`, `rucio rule remove`, …) without explicit user
confirmation. Several destructive variants (`rule remove`,
`did remove`, `replica remove`, `rse remove`, `account remove`,
`erase`) are denied by default in opencode's permissions. The MCP
rule-write tools (`rucio_add_rule`, `rucio_delete_rule`,
`rucio_update_rule`, `rucio_move_rule`, `rucio_reduce_rule`,
`rucio_approve_rule`, `rucio_deny_rule`) are disabled in this
config's `tools` block — never attempt them; route any write through
the CLI so the permission gate applies.

## Reference files

Read on demand, one level deep:

- **Authentication & credentials** — rucio.cfg search order, per-auth
  credential matrix, env vars, the prerequisite check that branches
  on `auth_type`: [reference/auth.md](reference/auth.md).
- **Full command catalogue** — every read-only and write subcommand
  with flags and legacy-to-v38 mapping: [reference/commands.md](reference/commands.md).

## Getting the CLI

On machines with the `sw.escape.eu` CVMFS mount, `rucio` is already
packaged:

```bash
export RUCIO_HOME=/cvmfs/sw.escape.eu/rucio/38.3.0
source "$RUCIO_HOME/setup-minimal.sh"
```

Pin a different version by changing the path (versions live under
`/cvmfs/sw.escape.eu/rucio/`). Off-CVMFS, `pip install rucio-clients`
works but the user is responsible for `rucio.cfg` and any VOMS/OIDC
tooling.

## Quick prereq check

```bash
command -v rucio >/dev/null 2>&1 || { echo "rucio CLI not on PATH"; exit 1; }
rucio whoami   # fails loudly if config or credential is missing
```

If `rucio whoami` fails, read `reference/auth.md` and follow the
auth-aware prerequisite block there (it branches on `auth_type`: VOMS
proxy for `x509_proxy`, nothing for `oidc`).

## CLI shape (Rucio 36+)

Rucio uses a noun-first layout: `rucio did list`, `rucio replica list
file`, `rucio rule add`. Top-level groups: `account`, `config`, `did`,
`download`, `lifetime-exception`, `opendata`, `replica`, `rse`, `rule`,
`scope`, `subscription`, `upload`. Direct commands: `whoami`, `ping`,
`test-server`. For the exhaustive list, see
[reference/commands.md](reference/commands.md). Use
`rucio <group> --help` if in doubt.

## Identifier conventions

A **DID** (Data IDentifier) is `<scope>:<name>`.

Common ATLAS scopes:

| Scope prefix | Meaning |
|---|---|
| `data15_13TeV` … `data18_13TeV` | Run 2 pp data |
| `data22_13p6TeV` … `data24_13p6TeV` | Run 3 pp data |
| `mc16_13TeV`, `mc20_13TeV`, `mc23_13p6TeV` | Monte Carlo campaigns |
| `user.<cernname>` | Per-user scope for analysis outputs |
| `group.phys-<group>` | Group-wide scope |
| `valid*` | Validation samples |

A DID can refer to a **file**, a **dataset** (a set of files), or a
**container** (a set of datasets). `rucio did show <did>` confirms
which.

## Command quick reference

Enough to cover ~90 % of read-only queries. For flags, other scopes,
or any write op, read [reference/commands.md](reference/commands.md).

| Intent | Command |
|---|---|
| Who am I? | `rucio whoami` |
| Search by pattern | `rucio did list '<scope>:<pattern>'` |
| DID type / size / status | `rucio did show <scope>:<name>` |
| Files in a dataset | `rucio did content list <scope>:<name>` |
| Metadata (xsec, filter eff) | `rucio did metadata list <scope>:<name> --plugin DID_COLUMN` |
| Where are the replicas? | `rucio replica list dataset <scope>:<name>` |
| Give me PFNs | `rucio replica list file <scope>:<name> --protocols root` |
| Who has rules on it? | `rucio rule list <scope>:<name>` |
| List RSEs | `rucio rse list` |
| Storage quota | `rucio account limit list <account>` |

Write ops needing user confirmation:

| Intent | Command |
|---|---|
| Replicate to my site | `rucio rule add <did> <n> '<rse-expr>'` |
| Pull files locally | `rucio download <did>` (consider `--nrandom 1` first) |
| Publish a user dataset | `rucio upload --scope user.<name> --rse <RSE> <files>` |

## Workflow

1. **Pick the transport** (table above). For reads, prefer the MCP
   server matching the user's VO; sanity-check identity with
   `rucio-<vo>_rucio_whoami`. For the CLI path: `rucio whoami`; if it
   fails, read `reference/auth.md`.
2. **Locate the DID**: `rucio_list_dids` (MCP) or `rucio did list
   '<scope>:<pattern>'`, then `rucio_get_did` / `rucio did show
   <scope>:<name>` to confirm type and size.
3. **Pick the follow-up** from the quick-reference table above, based
   on the user's intent (MCP↔CLI mapping in
   [reference/commands.md](reference/commands.md)).
4. **For writes and downloads**: switch to the CLI, show the exact
   command (including any RSE expression), and request explicit
   confirmation before running.

## Pitfalls

- **Quote** DIDs with glob characters
  (`'mc20_13TeV:*.Sherpa_*.DAOD_PHYSLITE.*'`) — the shell will
  otherwise mangle them.
- Rucio commands are **case-sensitive** on scope and name.
- `rucio did list` without `--filter type=...` can return files **and**
  containers with the same prefix.
- `rucio replica list dataset` can report incomplete replicas
  (`state=U`/`state=C`); those files aren't downloadable from that RSE.
- A container is not a dataset — `rucio did content list` on a
  container walks one level; use it recursively only when you mean to.
- `rucio download` uses `X509_USER_PROXY` when `auth_type = x509_proxy`;
  the default proxy at lxplus expires in 24 h, so long transfers can
  fail mid-way.
- DID naming differs between experiments — this skill is ATLAS-flavoured.
  CMS/LHCb scopes and datatype strings differ.

## Verification

A successful use of this skill ends with either:

- a printed DID (or list of DIDs) with confirmed type and byte size,
  and the user knowing where they can read it from; or
- a rule-id (for write operations), logged with the requesting
  account and the RSE expression used.
