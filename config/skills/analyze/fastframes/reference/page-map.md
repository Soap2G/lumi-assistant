# FastFrames docs page map (pinned: /latest/)

Base URL: https://atlas-project-topreconstruction.web.cern.ch/fastframesdocumentation/latest/
Source: MkDocs Material site, structure snapshotted from sitemap.xml (June 2026).
Mechanism: WebFetch the page whose topic matches the question; cite the public URL.
Re-snapshot on a version bump (see SKILL Version-bump procedure): GET `<base>sitemap.xml`.

## Top-level
| Topic | Page URL (append to base) |
|---|---|
| Landing / what FastFrames is | `` (the base itself) |
| Tutorial (end-to-end worked example) | `tutorial/` |
| Configuration reference (ALL config blocks/keys) | `configuration/` |
| Recommendations for running | `recommendations/` |
| Changelog (version-soft anchor — check here) | `changelog/` |

## Code flow / diagrams
| Topic | Page URL |
|---|---|
| Code-flow diagram (how the event loop is built) | `code_diagrams/code_flow/` |
| Usage diagram (the run-step flow) | `code_diagrams/usage/` |

## Documentation (per-topic)
| Topic | Page URL |
|---|---|
| Installation (asetup StatAnalysis + cmake build) | `documentation/installation/` |
| Metadata production (filelist + sum_of_weights) | `documentation/metadata_production/` |
| Custom classes (custom_frame_name, define columns) | `documentation/custom_classes/` |
| Histogramming (`--step h`, regions → histograms) | `documentation/histogramming/` |
| Ntupling (`--step n`, branches/selection/copy_trees) | `documentation/ntupling/` |
| Truth processing (particle/truth level) | `documentation/truth_processing/` |
| Unfolding (response/migration inputs) | `documentation/unfolding/` |
| Systematics (automatic_systematics, mapping) | `documentation/systematics/` |
| Cutflows | `documentation/cutflows/` |
| ONNX inference (simple_onnx_inference) | `documentation/onnx_inference/` |
| Distributed computing (split jobs, batch_submit.py, grid) | `documentation/distributed_computing/` |
| Helper functions | `documentation/helper_functions/` |
| TRExFitter integration (produce_trexfitter_config.py) | `documentation/trexfitter_integration/` |

## Event tutorials
| Topic | Page URL |
|---|---|
| Top Workshop 2025 tutorial | `eventtutorials/topws2025/Tutorial/` |

If the right page is unclear, fall back to:
`WebSearch: site:atlas-project-topreconstruction.web.cern.ch/fastframesdocumentation <query>`
then WebFetch the hit. The Doxygen code reference (separate site, linked from the repo)
is the last resort for C++ class internals.
