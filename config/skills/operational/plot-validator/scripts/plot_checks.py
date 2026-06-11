#!/usr/bin/env python3
"""Programmatic red-flag checks for an analysis figure.

This is the *mechanical* half of the plot-validator skill: the deterministic
checks a human (or a reviewer agent) should never have to eyeball. It does
NOT replace looking at the rendered image — the skill body tells you to do
both. What it catches: missing/blank figure files, data/MC ratios outside a
profile's band, empty or negative bins, zero-degree-of-freedom fits
(chi2/ndf = 0/0), bad goodness-of-fit, and the MeV/GeV axis-unit trap.

Thresholds are NOT hard-coded here. They are read from a YAML block in a
thresholds file (default: ../reference/thresholds.md), so a physics group can
retune them without touching this script. Pick a profile with --profile.

Inputs (any combination):
  --image <path>      a PNG/PDF figure file; checked for existence, non-zero
                      size, and (PDF) extractable text + declared axis units.
  --hist-json <path>  a JSON description of the histogram(s) and any fit; the
                      quantitative checks run on this.

The --hist-json schema (all keys optional except where a check needs them):
  {
    "x_unit": "GeV",                # declared x-axis unit
    "x_max": 250.0,                 # max x value plotted (for unit sanity)
    "quantity": "mass",             # hint that GeV-scale is expected
    "bins": [                       # per-bin data and MC
      {"data": 120, "mc": 110.0},
      {"data": 0,   "mc": 0.0},
      ...
    ],
    "fit": {"chi2": 0.0, "ndf": 0}  # optional fit result
  }

Output: a structured A/B/C report on stdout. Exit code is non-zero when any
Category A red flag fires, so the check can gate a pipeline.

Findings use the panel's canonical classes:
  A  blocking   — invalidates the figure as shown
  B  must-fix   — a real problem short of invalidating
  C  style      — presentation only
"""

import argparse
import json
import os
import re
import subprocess
import sys


# ---- threshold loading -----------------------------------------------------

def load_thresholds(path, profile):
    """Parse the fenced ```yaml block out of the thresholds markdown file and
    return the requested profile as a dict. We parse the fence ourselves so
    the script has no hard dependency on PyYAML being importable; if PyYAML is
    present we use it, otherwise we fall back to a tiny flat parser that
    handles the simple `key: value` shape this file uses."""
    with open(path, "r") as fh:
        text = fh.read()

    m = re.search(r"```yaml\s*\n(.*?)```", text, re.DOTALL)
    if not m:
        raise SystemExit(f"no ```yaml block found in {path}")
    block = m.group(1)

    profiles = _parse_yaml_block(block)
    if profile not in profiles:
        raise SystemExit(
            f"profile '{profile}' not in {path}; "
            f"available: {', '.join(sorted(profiles))}"
        )
    return profiles[profile]


def _parse_yaml_block(block):
    try:
        import yaml  # type: ignore
        return yaml.safe_load(block)
    except Exception:
        pass

    # Minimal fallback: top-level `name:` opens a profile; indented
    # `key: value` lines fill it; `#` comments and blanks ignored.
    profiles = {}
    current = None
    for raw in block.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1].strip()
            profiles[current] = {}
            continue
        if current is not None and ":" in line:
            key, _, val = line.strip().partition(":")
            profiles[current][key.strip()] = _coerce(val.strip())
    return profiles


def _coerce(val):
    low = val.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        return val


# ---- findings accumulator --------------------------------------------------

class Report:
    def __init__(self):
        self.findings = []  # (cls, title, detail)

    def add(self, cls, title, detail):
        self.findings.append((cls, title, detail))

    def has_blocking(self):
        return any(c == "A" for c, _, _ in self.findings)

    def emit(self):
        print("PLOT-VALIDATOR REPORT")
        print("=" * 60)
        order = {"A": 0, "B": 1, "C": 2}
        for cls in ("A", "B", "C"):
            rows = [f for f in self.findings if f[0] == cls]
            label = {"A": "A — blocking", "B": "B — must-fix",
                     "C": "C — style"}[cls]
            if not rows:
                continue
            print(f"\n[{label}]")
            for _, title, detail in rows:
                print(f"  [{cls}] {title}")
                if detail:
                    print(f"        {detail}")
        if not self.findings:
            print("\nNo programmatic red flags. (Still view the rendered "
                  "image — this script does not see what a human sees.)")
        print("\n" + "=" * 60)
        verdict = "RED FLAG (Category A present)" if self.has_blocking() \
            else "no blocking findings"
        print(f"RESULT: {verdict}")


# ---- image checks ----------------------------------------------------------

def check_image(path, report):
    if not os.path.exists(path):
        report.add("A", "figure file missing",
                   f"{path} does not exist — nothing was produced")
        return
    size = os.path.getsize(path)
    if size == 0:
        report.add("A", "figure file is empty",
                   f"{path} is 0 bytes")
        return

    if path.lower().endswith(".pdf"):
        text = _extract_pdf_text(path)
        if text is None:
            report.add("B", "could not extract PDF text",
                       "pdftotext and pypdf both unavailable/failed; "
                       "view the rendered image manually (see SKILL.md)")
        elif not text.strip():
            report.add("B", "PDF has no extractable text",
                       "axis labels/units may be rasterised; inspect the "
                       "rendered image directly")


def _extract_pdf_text(path):
    """AGENTS.md PDF recipe: pdftotext, then pypdf, then give up (None)."""
    try:
        out = subprocess.run(["pdftotext", path, "-"],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return out.stdout
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    try:
        import pypdf  # type: ignore
        r = pypdf.PdfReader(path)
        return "\n\n".join(p.extract_text() or "" for p in r.pages)
    except Exception:
        return None


# ---- histogram / fit checks ------------------------------------------------

def check_hist(hist, thr, report):
    bins = hist.get("bins", [])
    ratio_min = thr.get("data_mc_ratio_min")
    ratio_max = thr.get("data_mc_ratio_max")
    max_outliers = thr.get("max_outlier_bins", 0)
    allow_empty = thr.get("allow_empty_bins", False)

    outliers = []
    empty_data = 0
    for i, b in enumerate(bins):
        data = b.get("data")
        mc = b.get("mc")
        if data is not None and data < 0:
            report.add("A", f"negative data yield in bin {i}",
                       f"data={data} — unphysical")
        if mc is not None and mc < 0:
            report.add("A", f"negative MC yield in bin {i}",
                       f"mc={mc} — unphysical")
        if data == 0:
            empty_data += 1
        if mc and mc > 0 and data is not None:
            ratio = data / mc
            if (ratio_min is not None and ratio < ratio_min) or \
               (ratio_max is not None and ratio > ratio_max):
                outliers.append((i, ratio))

    if outliers:
        listed = ", ".join(f"bin {i} (ratio {r:.2f})" for i, r in outliers)
        if len(outliers) > max_outliers:
            report.add("A", "data/MC ratio out of band in too many bins",
                       f"{len(outliers)} bins outside "
                       f"[{ratio_min}, {ratio_max}] (max {max_outliers}): "
                       f"{listed}")
        else:
            report.add("B", "data/MC ratio out of band",
                       f"{listed} — within the {max_outliers}-bin tolerance "
                       f"but worth a look")

    if empty_data and not allow_empty:
        report.add("B", "empty data bins inside plotted range",
                   f"{empty_data} bin(s) with zero data; profile disallows "
                   f"empty bins")

    _check_fit(hist.get("fit"), thr, report)
    _check_units(hist, report)


def _check_fit(fit, thr, report):
    if not fit:
        return
    ndf = fit.get("ndf")
    chi2 = fit.get("chi2")
    min_ndf = thr.get("min_ndf", 1)
    if ndf is not None:
        if ndf <= 0:
            report.add("A", "fit has non-positive degrees of freedom",
                       f"ndf={ndf} (chi2/ndf = {chi2}/{ndf}) — a 0/0 or "
                       f"over-parametrised fit is meaningless")
            return
        if ndf < min_ndf:
            report.add("A", "fit below minimum degrees of freedom",
                       f"ndf={ndf} < min_ndf={min_ndf}")
            return
        if chi2 is not None:
            chi2_ndf = chi2 / ndf
            cap = thr.get("chi2_ndf_max")
            if cap is not None and chi2_ndf > cap:
                report.add("B", "poor goodness-of-fit",
                           f"chi2/ndf = {chi2_ndf:.2f} > {cap}")


def _check_units(hist, report):
    """MeV/GeV trap: a mass-like spectrum declared in MeV but plotted on a
    GeV-scale axis (or vice-versa). ATLAS PHYSLITE stores MeV; plotting in
    GeV needs /1000."""
    unit = (hist.get("x_unit") or "").strip()
    x_max = hist.get("x_max")
    quantity = (hist.get("quantity") or "").lower()
    if not unit or x_max is None:
        return
    mass_like = any(q in quantity for q in ("mass", "energy", "pt", "et",
                                            "momentum"))
    if not mass_like:
        return
    if unit.lower() == "mev" and x_max < 1000:
        report.add("B", "axis unit/scale mismatch (MeV declared, GeV range)",
                   f"x_unit='MeV' but x_max={x_max} looks GeV-scale; "
                   f"likely a missing /1000 (PHYSLITE is MeV)")
    if unit.lower() == "gev" and x_max > 100000:
        report.add("B", "axis unit/scale mismatch (GeV declared, MeV range)",
                   f"x_unit='GeV' but x_max={x_max} looks MeV-scale; "
                   f"likely a stray *1000 or un-converted PHYSLITE values")


# ---- main ------------------------------------------------------------------

def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    default_thr = os.path.join(here, "..", "reference", "thresholds.md")

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", help="path to a PNG/PDF figure file")
    ap.add_argument("--hist-json", help="path to a histogram/fit JSON file")
    ap.add_argument("--thresholds", default=default_thr,
                    help="thresholds markdown file (default: "
                         "../reference/thresholds.md)")
    ap.add_argument("--profile", default="default",
                    help="threshold profile name (default: default)")
    args = ap.parse_args(argv)

    if not args.image and not args.hist_json:
        ap.error("give at least one of --image / --hist-json")

    thr = load_thresholds(args.thresholds, args.profile)
    report = Report()
    print(f"(profile: {args.profile} from {os.path.normpath(args.thresholds)})\n")

    if args.image:
        check_image(args.image, report)
    if args.hist_json:
        with open(args.hist_json) as fh:
            hist = json.load(fh)
        check_hist(hist, thr, report)

    report.emit()
    return 2 if report.has_blocking() else 0


if __name__ == "__main__":
    sys.exit(main())
