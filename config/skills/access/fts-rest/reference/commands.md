# fts-rest command catalogue

Full reference for the `fts-rest-*` family. Skill body
([../SKILL.md](../SKILL.md)) covers the common 90 %; come here for
flags, JSON job-file schema, and output structure.

Throughout: assume `FTS_ENDPOINT=https://fts3-pilot.cern.ch:8446` is
exported and a valid X509 proxy is in place
(see [auth.md](auth.md) for the prereq block).

## fts-rest-whoami

Print the DN, VO, and delegation-id the FTS server sees for this proxy.

```bash
fts-rest-whoami -s "$FTS_ENDPOINT"
fts-rest-whoami -s "$FTS_ENDPOINT" -j   # JSON output
```

Non-zero exit means the server rejected the proxy (wrong VO, expired,
malformed). The first call any script should make.

## fts-rest-server-status

Health + queue lengths of the FTS3 server.

```bash
fts-rest-server-status -s "$FTS_ENDPOINT"
fts-rest-server-status -s "$FTS_ENDPOINT" -j
```

Useful when transfers are slow — a saturated server reports high
`activeCount` and queue depth.

## fts-rest-transfer-list

List jobs visible to the caller.

```bash
fts-rest-transfer-list -s "$FTS_ENDPOINT"                       # default: my own
fts-rest-transfer-list -s "$FTS_ENDPOINT" -o "$(whoami)"        # by submitter
fts-rest-transfer-list -s "$FTS_ENDPOINT" --state ACTIVE
fts-rest-transfer-list -s "$FTS_ENDPOINT" --state FAILED        # recent failures
fts-rest-transfer-list -s "$FTS_ENDPOINT" --source-se srm://… --dest-se davs://…
fts-rest-transfer-list -s "$FTS_ENDPOINT" --time-window 6       # last 6 h
```

Common flags:

| Flag | Meaning |
|---|---|
| `-o <user>` | Submitter (DN substring or username) — admin-only off-self |
| `--state <S>` | One of SUBMITTED, READY, ACTIVE, FINISHED, FINISHEDDIRTY, FAILED, CANCELED, STAGING, ARCHIVING |
| `--source-se`, `--dest-se` | Filter by SE URL prefix |
| `--time-window <H>` | Look-back in hours |
| `-j` | JSON output |

If the user lacks admin rights, `-o someoneelse` silently returns
*their own* jobs. Always confirm DN in the output if `-o` was used.

## fts-rest-transfer-status

Status of one job by its UUID.

```bash
fts-rest-transfer-status -s "$FTS_ENDPOINT" -j <job-id>                # job-level
fts-rest-transfer-status -s "$FTS_ENDPOINT" -j <job-id> --list-files   # per-file
fts-rest-transfer-status -s "$FTS_ENDPOINT" -j <job-id> --dump         # raw JSON
```

Per-file state codes: same as job, plus `NOT_USED` (alternate replica
that wasn't tried). For `FINISHEDDIRTY`, `--list-files` is the *only*
way to find which files failed and why.

## fts-rest-transfer-submit

Submit a new transfer job. **Write op — confirm before running.**

```bash
fts-rest-transfer-submit -s "$FTS_ENDPOINT" -f jobfile.json
fts-rest-transfer-submit -s "$FTS_ENDPOINT" -f jobfile.json --dry-run
```

The job file is **JSON** (not YAML):

```json
{
  "files": [
    {
      "sources":      ["srm://srm-atlas.cern.ch:8443/srm/managerv2?SFN=/eos/atlas/atlasdatadisk/rucio/foo.root"],
      "destinations": ["davs://eospublic.cern.ch:443/eos/user/me/foo.root"],
      "checksum":     "ADLER32:0abc1234",
      "filesize":     1048576,
      "metadata":     {"my-tag": "demo-2026"}
    }
  ],
  "params": {
    "verify_checksum":     true,
    "overwrite":           false,
    "retry":               1,
    "retry_delay":         60,
    "priority":            3,
    "max_time_in_queue":   3600,
    "copy_pin_lifetime":   -1,
    "bring_online":        -1,
    "job_metadata":        {"submitter": "alice", "campaign": "feb-2026"}
  }
}
```

Notes on the schema:

- `sources` and `destinations` are **arrays**; an entry with multiple
  sources lets FTS3 pick the first that succeeds.
- `checksum` is `<algo>:<hex>` — `ADLER32` is the most common, `MD5`
  and `CRC32` also supported. Omit only if `verify_checksum=false`.
- `priority` is 1–5 (5 = highest). Most users should leave it at the
  default (3).
- `bring_online` / `copy_pin_lifetime` are for tape SEs. Use `-1` to
  let the server decide.
- `metadata` and `job_metadata` are free-form JSON visible to ops.

Server returns `{"job_id": "<uuid>"}`; record the UUID before
returning to the user.

## fts-rest-transfer-cancel

Cancel a running job. **Write op — confirm before running.**

```bash
fts-rest-transfer-cancel -s "$FTS_ENDPOINT" -j <job-id>
fts-rest-transfer-cancel -s "$FTS_ENDPOINT" -j <job-id> --file <SE-URL>   # one file
```

The server flips the job to `CANCELED` (or the file to `CANCELED`
within an otherwise live job) within a few seconds. Files already
`FINISHED` are not rolled back.

## fts-rest-delete-submit

Submit a delete operation against an SE. **Write op — confirm.**

```bash
fts-rest-delete-submit -s "$FTS_ENDPOINT" -f deletefile.json
```

Job file:

```json
{
  "delete": [
    "srm://srm-atlas.cern.ch:8443/srm/managerv2?SFN=/eos/atlas/.../doomed.root",
    "davs://eospublic.cern.ch:443/eos/.../also-doomed.root"
  ]
}
```

Status / cancel use the same `transfer-status` / `transfer-cancel`
binaries against the returned `job_id`.

## fts-rest-delegate

Renew the user's delegation on the server. **Write op — confirm.**

```bash
fts-rest-delegate -s "$FTS_ENDPOINT"
fts-rest-delegate -s "$FTS_ENDPOINT" -H 96   # delegate for 96 hours
```

See [auth.md#delegation](auth.md) for when this is needed.

## fts-rest-ban

Admin-only: ban a user / DN / host / SE from this FTS server.
**Denied by default in opencode permissions.** Surface the user-asked
intent to the user verbatim and decline.

```bash
fts-rest-ban -s "$FTS_ENDPOINT" se --storage davs://bad-se.example/  --status WAIT
fts-rest-ban -s "$FTS_ENDPOINT" dn --user-dn '/DC=ch/.../CN=Bad Actor'
```

Sub-commands: `se` (ban an SE URL), `dn` (ban a DN). Status values
`WAIT` (queue but don't run) or `CANCEL` (kill in-flight) — read the
upstream docs (`fts-rest-ban --help`) before running.

## State machine reference

```
SUBMITTED -> READY -> ACTIVE -> FINISHED
                              \-> FINISHEDDIRTY   # some files failed
                              \-> FAILED          # all files failed
                              \-> CANCELED        # user cancelled
STAGING                                          # for tape sources (bring-online)
ARCHIVING                                        # for tape destinations
```

The same state vocabulary is used at both job and per-file level.
The job-level state is the worst-case rollup of its files.

## Verifying a successful run

After any submit, the skill body's verification rule is:

- Print the `job_id`.
- Poll with `fts-rest-transfer-status -j <id>` (no `--list-files`
  until you see `FINISHEDDIRTY` or `FAILED`).
- Stop when the state is terminal (`FINISHED`, `FINISHEDDIRTY`,
  `FAILED`, `CANCELED`). For `FINISHEDDIRTY` / `FAILED`, re-run with
  `--list-files` and report which sources / destinations failed and
  the error reason.
