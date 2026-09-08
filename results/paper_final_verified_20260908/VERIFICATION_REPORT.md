# XMON-Grid — Paper Final Verification Package

## Purpose

This directory records the clean, from-scratch verification used as the basis for the paper's quantitative results. It is intentionally separate from historical result directories and draft scientific-cleanup branches.

## Exact provenance

- Repository: `BurhanAbdullah/XMON-Grid`
- Branch at verification: `xmon-main`
- Commit: `6a58e2137860f742616ce62196b4bea255991b37`
- Verification branch: `paper-final-verified-20260908`
- Verification date: 2026-09-08
- No modifications to `core/` or `scripts/` were made for the verification.

## Commands executed

```text
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/run_independent_validation.py
python scripts/physical_sanity_check.py
```

The verification report records 20/20 unit tests passing and a clean 5-seed, 4-topology, 6,000-evaluation reproduction.

## Manuscript result check

The independently regenerated point estimates match the manuscript for the directly comparable detection metrics, including the five-seed K=2 results, ablations, detector comparisons, and ROC-AUC.

The regenerated physical sanity checks also pass for IEEE 9-, 14-, 30-, and 118-bus cases.

## Scientific handling

This package does not replace, improve, or selectively report results. It preserves the verified values and records their computational provenance. Historical result directories must not be substituted for this verification package when preparing the paper.

## Submission rule

Before final publication/tagging, use the exact commit and artifacts recorded here as the reproducibility reference. Do not alter reported numerical results merely to improve appearance or performance.
