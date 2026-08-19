#!/usr/bin/env python3
"""Apply and verify publication manuscript/code consistency edits.

Safe on both fresh and already-patched checkouts: known legacy forms are
rewritten when present, while missing legacy forms are accepted. The gate then
verifies the canonical equations, authoritative figure provenance, and absence
of superseded claims.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"

SEQ = r"A sequential threat accumulator $\Theta_k=\alpha\Theta_{k-1}+S_{\mathrm{comp},k}$ for persistent composite anomalies."
CUSUM_Z = r"z_k=\frac{\mathrm{NIS}_k-\mu_0}{\sigma_0}"
CUSUM_G = r"g_k=\max\left(0,g_{k-1}+z_k-\kappa\right)"
JITTER = r"J_k=\frac{|\Delta t_k-\mu_T|}{\sigma_T}"
COMPOSITE = r"S_{\mathrm{comp},k}=w_1S_{\mathrm{NIS},k}+w_2S_{\mathrm{CUSUM},k}+w_3S_{\mathrm{JITTER},k}"
FIGURES = "../results/authoritative_validation_20260815/paper_figures/"

LEGACY = [
    (r"A sequential innovation accumulator $\Theta(k)=0.9\Theta(k-1)+a_{\mathrm{nis}}(k)$ for persistent anomalies.", SEQ),
    (
        "The adaptive drift statistic is represented by\n\\begin{equation}\nS_k=\\max\\left(0,S_{\\mathrm{nis}}(k)+z_k-d\\right),\n\\end{equation}\nwhere $d$ is the drift allowance. A CUSUM alarm is generated when the calibrated threshold is exceeded.",
        "The NIS-based CUSUM first standardizes the innovation statistic using the benign calibration distribution,\n\\begin{equation}\n" + CUSUM_Z + ",\n\\end{equation}\nand then applies the one-sided recursion\n\\begin{equation}\n" + CUSUM_G + ",\n\\end{equation}\nwhere $\\kappa$ is the drift allowance and the alarm is $a_{\\mathrm{cusum},k}=\\mathbb{I}\\{g_k>\\tau_{\\mathrm{cusum}}\\}$. The baseline mean $\\mu_0$, standard deviation $\\sigma_0$, and alarm threshold are calibrated from benign data only.",
    ),
    (
        "The adaptive drift statistic is represented by\n\\begin{equation}\nS_k=\\max\\left(0,S_{k-1}+z_k-d\\right),\n\\end{equation}\nwhere $d$ is the drift allowance. A CUSUM alarm is generated when the calibrated threshold is exceeded.",
        "The NIS-based CUSUM first standardizes the innovation statistic using the benign calibration distribution,\n\\begin{equation}\n" + CUSUM_Z + ",\n\\end{equation}\nand then applies the one-sided recursion\n\\begin{equation}\n" + CUSUM_G + ",\n\\end{equation}\nwhere $\\kappa$ is the drift allowance and the alarm is $a_{\\mathrm{cusum},k}=\\mathbb{I}\\{g_k>\\tau_{\\mathrm{cusum}}\\}$. The baseline mean $\\mu_0$, standard deviation $\\sigma_0$, and alarm threshold are calibrated from benign data only.",
    ),
    (
        "Timing jitter is represented by\n\\begin{equation}\nJ_k=\\left|\\Delta t_k-\\overline{\\Delta t}\\right|,\n\\end{equation}\nwith a binary alarm when the calibrated jitter threshold is exceeded.",
        "Timing jitter is represented by the standardized instantaneous deviation\n\\begin{equation}\n" + JITTER + ",\n\\end{equation}\nwith a sliding-window mean\n\\begin{equation}\n\\overline{J}_k=\\frac{1}{W_k}\\sum_{i=k-W_k+1}^{k}J_i,\\qquad W_k=\\min(k,W).\n\\end{equation}\nThe binary jitter alarm is\n\\begin{equation}\na_{\\mathrm{jitter},k}=\\mathbb{I}\\{J_k>\\eta_\\sigma\\;\\wedge\\;\\overline{J}_k>\\eta_\\mu\\},\n\\end{equation}\nwhere $\\mu_T$ and $\\sigma_T$ are estimated from benign inter-arrival times and $\\eta_\\sigma,\\eta_\\mu$ are fixed detector limits.",
    ),
]


def apply() -> bool:
    text = PAPER.read_text(encoding="utf-8")
    original = text
    for old, new in LEGACY:
        if old in text:
            text = text.replace(old, new)

    old_seq_note = "The sequence threshold is calibrated from baseline data only, avoiding test-set threshold leakage."
    new_seq_note = (old_seq_note + " In the implementation, $\\alpha=0.90$ and the update uses the continuous "
                    "composite threat score $S_{\\mathrm{comp},k}$ rather than a binary detector flag.")
    if old_seq_note in text and "continuous composite threat score" not in text:
        text = text.replace(old_seq_note, new_seq_note, 1)

    if "\\subsection{Continuous Composite Threat Score}" not in text:
        marker = "\\subsection{Quorum Fusion}\n"
        block = ("\\subsection{Continuous Composite Threat Score}\n"
                 "The three detector streams are also mapped to a bounded continuous score. With normalized component "
                 "scores $S_{\\mathrm{NIS},k}$, $S_{\\mathrm{CUSUM},k}$, and $S_{\\mathrm{JITTER},k}$,\n"
                 "\\begin{equation}\n" + COMPOSITE + ",\\qquad \\sum_i w_i=1,\n"
                 "\\end{equation}\n"
                 "where the implementation uses $(w_1,w_2,w_3)=(0.50,0.30,0.20)$ and clips each component and the "
                 "final score to $[0,1]$.\n\n")
        if marker in text:
            text = text.replace(marker, block + marker, 1)

    text = text.replace("../results/independent_validation_run/paper_figures/", FIGURES)
    text = text.replace(
        "The present manuscript therefore does not retain the earlier claims of FPR below $0.6\\%$ or recall of $85.85\\%$ as authoritative results for this run.",
        "The present manuscript does not retain the earlier archived claims of sub-$0.6\\%$ FPR or the earlier high-recall aggregate as authoritative results for this run.",
    )
    text = text.replace("85.85\\% recall", "the earlier high-recall aggregate")
    text = text.replace("recall of $85.85\\%$", "the earlier high-recall aggregate")

    if text != original:
        PAPER.write_text(text, encoding="utf-8")
        return True
    return False


def verify() -> None:
    text = PAPER.read_text(encoding="utf-8")
    required = {
        "sequential accumulator": SEQ,
        "CUSUM standardization": CUSUM_Z,
        "CUSUM recursion": CUSUM_G,
        "jitter statistic": JITTER,
        "composite score": COMPOSITE,
        "authoritative figure path": FIGURES,
    }
    missing = [name for name, marker in required.items() if marker not in text]
    if missing:
        raise SystemExit("PUBLICATION CONSISTENCY FAILURE: " + ", ".join(missing))

    forbidden = [
        "85.85\\% recall",
        "recall of $85.85\\%$",
        "../results/independent_validation_run/paper_figures/",
        "0.58\\% FPR",
    ]
    stale = [token for token in forbidden if token in text]
    if stale:
        raise SystemExit("PUBLICATION STALE-CLAIM FAILURE: " + ", ".join(stale))


def main() -> None:
    changed = apply()
    verify()
    print("Publication manuscript consistency gate: PASS" + (" (updated)" if changed else " (already current)"))


if __name__ == "__main__":
    main()
