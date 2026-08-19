# XMON-Grid Project Validation Release

## Validation scope
- Canonical PYPOWER/MATPOWER benchmark definitions for IEEE 9-, 14-, 30-, and 118-bus cases.
- Independent Ybus cross-validation against PYPOWER.
- Analytical measurement/Jacobian checks against finite differences.
- Model/unit tests and cross-case regression tests.
- Physical AC network consistency audit.
- Seeded reproducibility and release-artifact checks.

## Current publication-data provenance
The single current paper-facing numerical authority is:

`results/authoritative_validation_20260815/`

This package is generated from the corrected five-seed experiment and contains the detector trace, regenerated tables, retained figures, figure manifest, physical-sanity data, and SHA256 manifest.

Historical validation directories remain available for provenance but must not be used as current publication data.

## Important scope limitation
This identifies a validated computational benchmark state. It does not imply hardware, HIL, field, or real-world operational validation.
