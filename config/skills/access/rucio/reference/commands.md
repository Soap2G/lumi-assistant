# Rucio command catalogue (v38+)

Full list of read-only and write commands in the noun-verb v36+ CLI
layout. Read this file when you need a specific command, flag, or
want to confirm a mapping from a legacy flat verb.

Authoritative upstream source:
https://github.com/rucio/rucio/tree/master/lib/rucio/cli

## Contents
- MCP tool ↔ CLI command mapping
- CLI shape and top-level groups
- Read-only commands (identity, RSEs, DIDs, metadata, replicas, rules, accounts, scopes, replica state)
- Write operations (data movement, DID lifecycle, rules, replicas, admin-level)

## MCP tool ↔ CLI command mapping

The `rucio-atlas` / `rucio-cms` / `rucio-escape` / `rucio-fcc` MCP
servers ([kratsg/rucio-mcp](https://github.com/kratsg/rucio-mcp))
expose the read surface as tools named `<server>_<tool>`, e.g.
`rucio-atlas_rucio_list_dids`. The tool names mirror the *deprecated*
flat-verb CLI — never copy them into a shell command.

| Intent | MCP tool | CLI (v38 noun-verb) |
|---|---|---|
| Identity | `rucio_whoami`, `rucio_ping` | `rucio whoami`, `rucio ping` |
| Search DIDs | `rucio_list_dids` | `rucio did list '<scope>:<pattern>'` |
| DID type/size/status | `rucio_get_did` | `rucio did show <did>` |
| Children of a collection | `rucio_list_content`, `rucio_list_files` | `rucio did content list <did>` |
| Parents | `rucio_list_parent_dids` | `rucio did show <did>` |
| Metadata | `rucio_get_metadata` | `rucio did metadata list <did>` |
| File replicas / PFNs | `rucio_list_replicas` | `rucio replica list file <did>` |
| Dataset/container replicas | `rucio_list_dataset_replicas`, `rucio_list_container_replicas` | `rucio replica list dataset <did>` |
| Rules on a DID | `rucio_list_did_rules` | `rucio rule list <did>` |
| Rule detail / history | `rucio_get_replication_rule`, `rucio_list_rule_history` | `rucio rule show <rule_id>`, `rucio rule history <rule_id>` |
| RSEs | `rucio_list_rses`, `rucio_get_rse`, `rucio_list_rse_attributes`, `rucio_get_rse_usage` | `rucio rse list`, `rucio rse show <RSE>`, `rucio rse attribute list <RSE>` |
| Quotas / account | `rucio_get_local_account_limits`, `rucio_get_local_account_usage`, `rucio_get_account` | `rucio account limit list <a>`, `rucio account show <a>` |
| Scopes | `rucio_list_scopes`, `rucio_list_scopes_for_account` | `rucio scope list` |
| Subscriptions | `rucio_list_subscriptions`, `rucio_list_subscription_rules` | `rucio subscription list` |
| Dataset locks | `rucio_get_dataset_locks`, `rucio_get_dataset_locks_by_rse` | *(no direct v38 CLI equivalent)* |
| Download / upload | **none — CLI only** | `rucio download <did>`, `rucio upload …` |
| Rule writes | **disabled in this config** | `rucio rule add/move/update/remove` (confirmation-gated) |

## CLI shape

Rucio reorganised its CLI from flat verbs (`list-dids`, `list-files`,
`add-rule`) to a noun-first, verb-second layout (`rucio did list`,
`rucio replica list file`, `rucio rule add`). The legacy flat commands
still exist for a transition period under `rucio-admin`/`bin_legacy`
but should not be emitted.

Top-level groups: `account`, `config`, `did`, `download`,
`lifetime-exception`, `opendata`, `replica`, `rse`, `rule`, `scope`,
`subscription`, `upload`. Direct top-level commands: `whoami`, `ping`,
`test-server`.

Use `rucio <group> --help` and `rucio <group> <subgroup> --help` to
discover flags before invoking.

## Read-only commands

### Identity and sanity
- `rucio whoami` — account, identity, e-mail on the active token.
- `rucio ping` — confirm the CLI can reach the server.
- `rucio test-server` — richer client/server connectivity check.

### Storage elements (RSEs)
- `rucio rse list` — all registered RSEs.
- `rucio rse show <RSE>` — usage, protocols, settings, attributes.
- `rucio rse attribute list <RSE>` — attributes only.
- `rucio rse distance show <SOURCE-RSE> <DEST-RSE>` — transfer distance.
- `rucio rse qos list <RSE>` — QoS policies for the RSE.

### DID discovery
- `rucio did list '<scope>:<pattern>'` — glob-style search.
  Quote the argument to stop the shell expanding `*`.
- `rucio did show <scope>:<name>` — attributes, status, parents for a
  DID (replaces legacy `stat` and `list-parent-dids`).
- `rucio did content list <scope>:<name>` — immediate children of a
  collection-type DID (files in a dataset, datasets in a container).
- `rucio did content history <scope>:<name>` — historical content of a
  collection-type DID.

### DID metadata
- `rucio did metadata list <scope>:<name>` — all metadata for one or
  more DIDs (replaces legacy `get-metadata`). Use `--plugin <name>`
  to target experiment-specific stores (ATLAS: `DID_COLUMN` for
  enriched metadata such as cross-section and filter efficiency).

### Replicas
- `rucio replica list file <scope>:<name>` — per-file PFNs. Available
  replicas only by default. Use flags like `--rses <RSE>` or
  `--protocols root` to filter (run `--help` for the full list in your
  installed version).
- `rucio replica list dataset <scope>:<name>` — per-RSE dataset
  replica summary with completeness state.

### Rules (transfer policy)
- `rucio rule list <scope>:<name>` — rules on a DID.
  Also accepts filters for account / file / subscription.
- `rucio rule show <rule_id>` — rule detail. Add `--examine` (or the
  equivalent flag reported by `--help`) for detailed transfer-error
  analysis.
- `rucio rule history <scope>:<name>` — history of rules acting on a
  DID.

### Accounts and quotas
- `rucio account list` — accounts matching a filter.
- `rucio account show <account>` — account info.
- `rucio account limit list <account>` — storage usage, quota, and
  remaining quota per RSE (replaces legacy `list-account-limits` and
  `list-account-usage`).
- `rucio account attribute list <account>` — key/value attributes.
- `rucio account identity list <account>` — auth identities.

### Scopes and subscriptions
- `rucio scope list` — existing scopes (filter by account with `--account`).
- `rucio subscription list` — subscriptions (use `--help` to confirm
  exact flags in your version).

### Replica state
- `rucio replica state list` — replicas by state (e.g. suspicious).

## Write operations (require explicit user confirmation)

### Data movement (top-level)
- `rucio download <scope>:<name>` — pull files to `./<scope>/<name>/`.
  Warn about size; suggest `--nrandom 1` for a sample. Useful flags:
  `--dir`, `--rses <RSE-expression>`, `--protocol`, `--ndownloader`,
  `--no-subdir`, `--ignore-checksum`, `--transfer-timeout`,
  `--nrandom`, `--pfn`, `--allow-tape`.
- `rucio upload --scope user.<name> --rse <RSE> <files>` — publish
  local files; confirm scope and RSE.

### DID lifecycle
- `rucio did add <scope>:<name> --type {dataset,container}` — create a
  new collection.
- `rucio did update <scope>:<name> ...` — touch, set last-accessed,
  open/close.
- `rucio did remove <scope>:<name>` — mark for expiry (deletion
  within ~24 h). **Denied by default in opencode permissions.**
- `rucio did content add <scope>:<name> --dids <child>` — attach DIDs.
- `rucio did content remove <scope>:<name> --dids <child>` — detach.
  **Denied by default.**
- `rucio did metadata add/remove <scope>:<name> --key <k> --value <v>`.
  Remove is **denied by default.**

### Rules
- `rucio rule add <scope>:<name> <copies> <RSE-expression>` — request
  replication. Always show the computed expression
  (e.g. `type=DATADISK&site=CERN`) before executing.
- `rucio rule remove <rule_id>` — release replicas; irreversible for
  the last rule on a dataset. **Denied by default.**
- `rucio rule update <rule_id> ...` — change expiry, lifetime, state.
- `rucio rule move <rule_id> <RSE-expression>` — create a child rule
  on a different RSE (parent is deleted once the child reaches OK).

### Replicas
- `rucio replica remove <scope>:<name>` — tombstone a replica.
  **Denied by default.**
- `rucio replica state update bad/unavailable/quarantine ...` — flag
  replica state problems.

### RSEs, accounts, scopes (admin-level)
- `rucio rse add/remove/update ...`, `rucio rse attribute add/remove`,
  `rucio rse protocol add/remove`, `rucio rse limit add/remove`,
  `rucio rse qos add/remove`, `rucio rse distance add/remove/update`.
- `rucio account add/remove/update`, `rucio account attribute add/remove`,
  `rucio account limit add/remove`, `rucio account identity add/remove`.
- `rucio scope add/update`.

These typically require admin privileges. All `remove` variants are
**denied by default** in opencode permissions. Do not invoke without
confirmation and without checking the user is allowed to run them.
