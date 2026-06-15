# Provenance — vendored MadGraph docs

Source:  MadGraphTeam/MadAgents `src/madagents/software_instructions/madgraph/`
Pin:     cf387c2c04a4c629ad9ec636f58a340563979c5c (2026-06-08, `main`)
License: MIT — paper arXiv:2601.21015 (Plehn, Schiller, Schmal)
Files:   27 topic docs, snapshot (verbatim + provenance header).

Refresh (deliberate, not CI): bump SHA/DATE in
`script/vendor/snapshot_madgraph_docs.sh`, re-run it, review the diff, commit,
and update the skill's Topic index + Version-bump section if the topic set
changed. This corpus is intentionally NOT wired into
`script/sync_vendored.py --check`: the upstream is slow-moving (2 commits in
5 months) and its internal layout is unstable, so a live drift-check would 404
on a reorg and nag for nothing. Pull, don't push.
