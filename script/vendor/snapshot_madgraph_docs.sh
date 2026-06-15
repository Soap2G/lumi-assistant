#!/usr/bin/env bash
# Snapshot the curated MadGraph docs from MadGraphTeam/MadAgents at a pin.
# Refresh = bump SHA/DATE below, re-run, review the diff, commit. NOT run in CI.
set -euo pipefail
SHA=cf387c2c04a4c629ad9ec636f58a340563979c5c
DATE=2026-06-08
REPO=https://github.com/MadGraphTeam/MadAgents
SRCDIR=src/madagents/software_instructions/madgraph
DEST=config/skills/reference/madgraph/reference
RAW=https://raw.githubusercontent.com/MadGraphTeam/MadAgents/${SHA}/${SRCDIR}

FILES=(installation process-syntax models-and-restrictions cards-and-parameters
  scripted-execution interactive-mode nlo-computations nlo-plugins-and-loops
  matching-and-merging coupling-orders-and-validation decays-and-madspin
  complex-mass-scheme pythia8-interface delphes-interface madanalysis5
  lhe-output-format pdfs-and-scales parameter-scans lepton-photon-colliders
  systematics-reweighting diagram-filtering biased-event-generation eft-smeftsim
  maddm-dark-matter maddm-cards-and-scans standalone-matrix-elements troubleshooting)

mkdir -p "$DEST"
for f in "${FILES[@]}"; do
  body="$(curl -fsSL "${RAW}/${f}.md")"
  {
    printf '<!-- Vendored from %s @ %s on %s.\n' "$REPO" "$SHA" "$DATE"
    printf '     Upstream path: %s/%s.md\n' "$SRCDIR" "$f"
    printf '     Curated MadGraph docs (MIT, arXiv:2601.21015). Snapshot — do not\n'
    printf '     hand-edit; refresh via script/vendor/snapshot_madgraph_docs.sh. -->\n'
    printf '%s\n' "$body"
  } > "${DEST}/${f}.md"
done
echo "wrote ${#FILES[@]} files to ${DEST}"
