# TopCPToolkit docs page map (pinned: /latest/)

Base URL: https://topcptoolkit.docs.cern.ch/latest/
Retrieval: PRIMARY = cerndocs MCP `search_docs(query, source="topcptoolkit")` then
`fetch_doc(url, source="topcptoolkit", mode=...)`. FALLBACK = WebFetch the base+path below.
Source: MkDocs Material; structure snapshotted from sitemap.xml (June 2026).
Re-snapshot on a version bump: GET `<base>sitemap.xml`.

## Getting started
| Topic | Path |
|---|---|
| Landing / what TopCPToolkit is | `` |
| Installation (asetup release 25 + build) | `starting/installation/` |
| Running locally (`runTop_el.py`) | `starting/running_local/` |
| Running on the grid | `starting/running_grid/` |
| Defining an analysis | `starting/analysis/` |
| Multiple selections | `starting/multiple_selections/` |
| Best practices | `starting/best_practices/` |
| Changelog (version-soft anchor) | `changelog/` |
| FAQ | `faq/` |

## Settings (the YAML CP-algorithm blocks)
| Block | Path |
|---|---|
| Config flags (global) | `settings/configflags/` |
| Electrons | `settings/electrons/` |
| Muons | `settings/muons/` |
| Photons | `settings/photons/` |
| Taus | `settings/taus/` |
| Jets | `settings/jets/` |
| Tracks | `settings/tracks/` |
| Missing ET | `settings/met/` |
| Trigger | `settings/trigger/` |
| Overlap removal | `settings/overlap/` |
| Object selection | `settings/objectselection/` |
| Event-level scale factors | `settings/scalefactors/` |
| Event selection | `settings/eventselection/` |
| Event reconstruction | `settings/reconstruction/` |
| Truth content | `settings/truth/` |
| Output ntuple (ntupling) | `settings/ntupling/` |
| ONNX wrapper | `settings/onnxwrapper/` |
| Experimental | `settings/experimental/` |
| Other blocks & methods | `settings/others/` |
| Settings index | `settings/` |

## Tutorials
| Topic | Path |
|---|---|
| Tutorials index | `tutorials/` |
| Setup | `tutorials/setup/` |
| Write your first config | `tutorials/write_config/` |
| Write an algorithm | `tutorials/write_algorithm/` |
| Submit to the grid | `tutorials/submit_grid/` |
| Machine learning | `tutorials/machine_learning/` |

## Contributing
| Topic | Path |
|---|---|
| Contributing / propose algorithm / report bug / request feature / suggest improvement | `contributing/` (+ subpages) |

Fallback search: `WebSearch: site:topcptoolkit.docs.cern.ch <query>`.
C++ algorithm internals live in the athena `PhysicsAnalysis/Algorithms` source.
