# XMON-Grid Project Validation Release

## Frozen commit
`c0ad960bcf8996df63cafd35546a22de6e63bc6c`

## Validation scope
- Canonical PYPOWER/MATPOWER benchmark definitions for IEEE 9-, 14-, 30-, and 118-bus cases.
- Independent Ybus cross-validation against PYPOWER.
- Analytical measurement/Jacobian checks against finite differences.
- Model/unit tests and cross-case regression tests.
- Physical AC network consistency audit.
- Seeded reproducibility and release-artifact checks.
- Existing manuscript deliberately excluded from project-only release gate.

## Paper-data provenance
The paper-facing numerical artifacts currently associated with the validated project are under `results/independent_validation_run/`, including the five-seed summary, comparative results, ablations, figures, and SHA256 manifest.

## Important scope limitation
The tag identifies a validated computational project state. It does not imply hardware, HIL, field, or real-world validation.
