# fts-rest auth & endpoint reference

How `fts-rest-*` authenticates and where to point it. Read this when
`fts-rest-whoami` fails or the user is unsure which endpoint to use.

## Auth model: X509 proxy

FTS3 uses **X509 client certificates** (a VOMS proxy in practice). The
CLI does not read any config file — every call takes the endpoint via
`-s <URL>` and pulls the proxy from one of:

1. `$X509_USER_PROXY` if set
2. `/tmp/x509up_u$(id -u)` (the GSI default location)

If both are unset / missing, the binary aborts with `Failed to load
client certificate`. There is no Bearer / SSO / OIDC mode in the
mainstream `fts-rest-*` builds (FTS3 itself supports OAuth2 tokens
server-side, but the REST CLI binaries here are X509-only).

## Generating a proxy

```bash
voms-proxy-init -voms atlas:/atlas        # ATLAS members
voms-proxy-init -voms cms:/cms            # CMS members
voms-proxy-init -voms lhcb:/lhcb          # LHCb members
voms-proxy-init -voms dteam:/dteam        # WLCG test VO
```

The result lives at `/tmp/x509up_u$(id -u)` by default and lasts ~24 h.
For longer-running scripts, point `X509_USER_PROXY` at a renewed
proxy file (`voms-proxy-init -valid 96:0 -out ~/myproxy`).

## Inspecting the proxy

```bash
voms-proxy-info -e -v        # exit non-zero if expired
voms-proxy-info -all          # full DN + VO + lifetime
```

The DN that comes back from `fts-rest-whoami` must match
`voms-proxy-info -i 'subject'`. If the user has multiple certs (e.g.
both a grid cert and a local cert), `X509_USER_CERT` /
`X509_USER_KEY` may need to be set explicitly before
`voms-proxy-init`.

## Picking the FTS endpoint

There is no single "FTS server" — each VO and tier of service runs
its own. The endpoint URL is the same shape:
`https://<host>.cern.ch:8446`.

| Endpoint | VO / Use |
|---|---|
| `https://fts3-pilot.cern.ch:8446` | Pilot / pre-prod for any VO; used by devops + integration testing |
| `https://fts3-public.cern.ch:8446` | CERN production for non-experiment VOs |
| `https://fts3-atlas.cern.ch:8446` | ATLAS production |
| `https://fts3-cms.cern.ch:8446` | CMS production |
| `https://fts3-lhcb.cern.ch:8446` | LHCb production |
| `https://fts3-alice.cern.ch:8446` | ALICE production |

For sites running their own FTS3 (BNL, FNAL, ASGC, …), the URL is
whatever that site publishes — `fts-rest-whoami -s <URL>` will
authorize the proxy or 403 cleanly.

Set it via env var to avoid repeating `-s` on every call:

```bash
export FTS_ENDPOINT=https://fts3-atlas.cern.ch:8446
fts-rest-whoami -s "$FTS_ENDPOINT"
```

The CLI does **not** read `FTS_ENDPOINT` itself; the env var here is a
convenience that the skill body passes into `-s`. Don't suggest
`unset FTS_ENDPOINT` as a recovery — it has no effect on the binary.

## Auth-aware prereq block

Drop this into a script (or run inline) before any FTS call:

```bash
command -v fts-rest-whoami >/dev/null 2>&1 || {
  echo "fts-rest CLI not on PATH (need fts-rest-client RPM or pip install fts3)"
  exit 1
}
: "${FTS_ENDPOINT:?FTS_ENDPOINT not set (e.g. https://fts3-pilot.cern.ch:8446)}"
voms-proxy-info -e -v >/dev/null 2>&1 || {
  echo "no valid X509 proxy; run voms-proxy-init -voms <VO>"
  exit 1
}
fts-rest-whoami -s "$FTS_ENDPOINT" >/dev/null || {
  echo "FTS authorization failed at $FTS_ENDPOINT"
  echo "  - is your proxy from a VO the server accepts?"
  echo "  - is the endpoint URL right for that VO?"
  exit 1
}
```

## Delegation

The FTS server needs its own copy of the proxy to drive transfers on
the user's behalf — that's what **delegation** is. The CLI does it
implicitly on `transfer-submit`, but it can also be done explicitly:

```bash
fts-rest-delegate -s "$FTS_ENDPOINT"        # renew delegation now
fts-rest-delegate -s "$FTS_ENDPOINT" -H 96  # delegate for 96 hours
```

Symptoms of a stale delegation: `transfer-submit` succeeds but the
job stalls in `SUBMITTED` and the per-file error mentions
`expired delegation`. Fix: re-`delegate` and either let the existing
job retry, or `transfer-cancel` + re-submit.

## Off-CERN: pip install

```bash
pip install fts3
```

This installs the same `fts-rest-*` binaries under whatever Python
prefix is active. The auth model is unchanged; you still need a VOMS
proxy and a reachable FTS endpoint.

Note: the PyPI package is `fts3`, but the binaries it ships are all
`fts-rest-*`. That's an upstream naming legacy, not a bug.
