# Final validation snapshot — 2026-08-14

This directory contains the text-form numerical snapshot corresponding to the successful GitHub Actions Scientific Validation run `31797631940` on commit `4310dc68a2adecf2106264ceab862bd016cfdd7c`.

The complete CI artifact digest was:

`sha256:99cd693611ffd692f61229b8a12f41a1926bcbfb32eb41781a20f20fc8fb6b23`

## Validation status

- Canonical IEEE 9/14/30/118 benchmark definitions: PASS.
- Local Ybus versus PYPOWER: PASS.
- Analytical Jacobian finite-difference cross-check: PASS; maximum error `2.666e-09`.
- Model unit tests: 16/16 PASS.
- Independent physical power-flow audit: PASS.
- Five-seed regeneration: PASS.
- Publication figure regeneration: PASS.
- Reproducibility-contract validation: PASS.

## Physical audit

The physical audit includes line charging, transformer tap/phase-shift terms, and normalization of solved angles to the model's bus-1 reference. The maximum absolute audited error across IEEE 9/14/30/118 is approximately `2.91e-14`.

## Important interpretation

The five-seed $K=2$ aggregate is F1 `0.9204 +/- 0.0026`, recall `0.8850 +/- 0.0012`, FPR `0.1525 +/- 0.0197`, and MCC `0.6667 +/- 0.0151`. Earlier archived aggregates with FPR below 0.6% are not the authoritative values for this regenerated experiment.
