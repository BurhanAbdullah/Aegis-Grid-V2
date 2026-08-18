#!/usr/bin/env python3
"""Idempotently harden retained figure captions for IEEE Transactions review.

Only known generic captions are replaced. If a caption is already hardened,
the script verifies the hardened text is present and makes no further change.
It never changes scientific values or results.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"

REPLACEMENTS = {
    "Overall detection-performance comparison for the primary validation set.":
        "Overall detector comparison computed from the authoritative detector trace ($N=6,000$ evaluations; 2,400 positive and 3,600 negative labels). Bars report F1-score, recall, and false-positive rate for each detector stream and quorum mode; numerical labels give the corresponding point estimates.",
    "$K=1$ versus $K=2$ operating-point trade-off using the validated detector outputs and five-seed aggregate summary.":
        "$K=1$ versus $K=2$ operating-point trade-off. The diamond is the primary-trace $K=1$ OR rule; individual circles are the five independent $K=2$ seeds; the larger point and error bars show the five-seed mean $\\pm$ sample standard deviation. $K=2$ is the strict majority of the three binary detector streams.",
    "ROC curve for the continuous composite threat score.":
        "Receiver-operating-characteristic curve for the continuous composite threat score $S_{\\mathrm{comp}}$, evaluated over all 6,000 authoritative test evaluations. The legend reports ROC-AUC; the dashed diagonal denotes chance discrimination. Class counts are stated in the panel.",
    "Precision--recall curve for the continuous composite threat score.":
        "Precision--recall curve for the continuous composite threat score $S_{\\mathrm{comp}}$, evaluated over all 6,000 authoritative test evaluations. The legend reports PR-AUC and the dashed horizontal line gives the positive-class prevalence baseline.",
    "Five-seed mean F1 performance across the four IEEE benchmark topologies.":
        "Topology-wise $K=2$ F1-score across IEEE 9-, 14-, 30-, and 118-bus benchmarks. Bars are five-seed means; error bars are the authoritative 95\\% confidence intervals. Each topology contributes 1,500 evaluations (300 per seed).",
    "Five-seed mean F1 and recall across the validated attack scenarios.":
        "Attack-wise $K=2$ performance for branch outage, FDIA, load shift, and stealth drift. F1 bars use authoritative 95\\% confidence intervals; recall bars use five-seed standard deviations. Each scenario contributes 1,200 evaluations (240 per seed); the benign baseline is excluded from the attack comparison.",
    "Detection robustness across attack severity tiers.":
        "Detection robustness of the $K=2$ quorum rule across the empirical attack-severity tiers in the authoritative detector trace. Bar labels report detection rate and the panel reports the number of positive evaluations contributing to each tier.",
    "AC power-flow numerical consistency across the canonical benchmark systems.":
        "Independent AC power-flow consistency check for the canonical IEEE benchmark systems. The plotted quantities are the maximum absolute active-power residual, maximum absolute reactive-power residual, and absolute network power-balance residual reconstructed from the canonical admittance model; values are shown on a logarithmic scale in per-unit.",
}


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    changed = 0
    already = 0
    missing = []
    for old, new in REPLACEMENTS.items():
        if old in text:
            text = text.replace(old, new)
            changed += 1
        elif new in text:
            already += 1
        else:
            missing.append(old)
    if missing:
        raise SystemExit(
            f"Caption hardening incomplete: missing {len(missing)} expected captions: {missing}"
        )
    if changed:
        PAPER.write_text(text, encoding="utf-8")
    print(f"Caption hardening verified: replaced={changed}, already_hardened={already}, total={len(REPLACEMENTS)}")


if __name__ == "__main__":
    main()
