# plot-validator thresholds

The numeric thresholds the validator applies live **here**, not in the
script — so a physics group can tune them without touching code, and so
different measurement types can carry different bounds (a precision
cross-section tolerates a tighter data/MC band than an early search).

`scripts/plot_checks.py` parses the fenced `yaml` block below. Each top-level
key is a **profile**; pick one with `--profile <name>` (default: `default`).
Add a profile by copying `default` and adjusting — do not bake numbers into
the script.

```yaml
default:
  # data/MC agreement, per bin (only bins with MC > 0 are tested)
  data_mc_ratio_min: 0.5
  data_mc_ratio_max: 2.0
  # how many bins may sit outside [min, max] before it is a red flag (A);
  # 1..this many out-of-band bins is a must-fix (B)
  max_outlier_bins: 2
  # goodness-of-fit
  chi2_ndf_max: 5.0
  # a fit with fewer than this many degrees of freedom is a red flag (A).
  # ndf <= 0 (e.g. chi2/ndf = 0/0) is always a red flag.
  min_ndf: 1
  # empty data bins inside the plotted range: false => flag them (B)
  allow_empty_bins: false

cross_section:
  # precision measurement: tighter band, stricter GoF
  data_mc_ratio_min: 0.7
  data_mc_ratio_max: 1.4
  max_outlier_bins: 1
  chi2_ndf_max: 3.0
  min_ndf: 1
  allow_empty_bins: false

search:
  # early/blinded search: looser band tolerated in control regions
  data_mc_ratio_min: 0.3
  data_mc_ratio_max: 3.0
  max_outlier_bins: 3
  chi2_ndf_max: 8.0
  min_ndf: 1
  allow_empty_bins: true
```

## Notes

- **`min_ndf` / zero-dof fits.** `ndf = n_data_points - n_free_parameters`.
  A fit reporting `ndf <= 0` is mathematically meaningless (the
  `chi2/ndf = 0/0` failure seen in the wild) and is always a Category A red
  flag, independent of the profile.
- **Unit sanity.** If a histogram declares its x-axis unit as `MeV` while a
  mass-like spectrum's range looks like GeV-scale numbers (max < 1000), the
  validator raises a must-fix — a common MeV↔GeV mistake (ATLAS PHYSLITE is
  MeV; plotting in GeV needs `/1000`).
- Bump a threshold by editing the value here and committing; the change
  ships on the next CVMFS publish. The script never overrides these.
