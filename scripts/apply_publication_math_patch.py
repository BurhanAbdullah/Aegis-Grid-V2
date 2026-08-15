#!/usr/bin/env python3
"""Apply exact, auditable paper/code consistency edits before publication build."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
REPLACEMENTS = [
    ("A sequential innovation accumulator $\\Theta(k)=0.9\\Theta(k-1)+a_{\\mathrm{nis}}(k)$ for persistent anomalies.", "A sequential threat accumulator $\\Theta_k=\\alpha\\Theta_{k-1}+S_{\\mathrm{comp},k}$ for persistent composite anomalies."),
    ("The adaptive drift statistic is represented by\n\\begin{equation}\nS_k=\\max\\left(0,S_{k-1}+z_k-d\\right),\n\\end{equation}\nwhere $d$ is the drift allowance. A CUSUM alarm is generated when the calibrated threshold is exceeded.", "The NIS-based CUSUM first standardizes the innovation statistic using the benign calibration distribution,\n\\begin{equation}\nz_k=\\frac{\\mathrm{NIS}_k-\\mu_0}{\\sigma_0},\n\\end{equation}\nand then applies the one-sided recursion\n\\begin{equation}\ng_k=\\max\\left(0,g_{k-1}+z_k-\\kappa\\right),\n\\end{equation}\nwhere $\\kappa$ is the drift allowance and the alarm is $a_{\\mathrm{cusum},k}=\\mathbb{I}\\{g_k>\\tau_{\\mathrm{cusum}}\\}$. The baseline mean $\\mu_0$, standard deviation $\\sigma_0$, and alarm threshold are calibrated from benign data only."),
    ("Timing jitter is represented by\n\\begin{equation}\nJ_k=\\left|\\Delta t_k-\\overline{\\Delta t}\\right|,\n\\end{equation}\nwith a binary alarm when the calibrated jitter threshold is exceeded.", "Timing jitter is represented by the standardized instantaneous deviation\n\\begin{equation}\nJ_k=\\frac{|\\Delta t_k-\\mu_T|}{\\sigma_T},\n\\end{equation}\nwith a sliding-window mean\n\\begin{equation}\n\\overline{J}_k=\\frac{1}{W_k}\\sum_{i=k-W_k+1}^{k}J_i,\\qquad W_k=\\min(k,W).\n\\end{equation}\nThe binary jitter alarm is\n\\begin{equation}\na_{\\mathrm{jitter},k}=\\mathbb{I}\\{J_k>\\eta_\\sigma\\;\\wedge\\;\\overline{J}_k>\\eta_\\mu\\},\n\\end{equation}\nwhere $\\mu_T$ and $\\sigma_T$ are estimated from benign inter-arrival times and $\\eta_\\sigma,\\eta_\\mu$ are fixed detector limits."),
    ("The sequence threshold is calibrated from baseline data only, avoiding test-set threshold leakage.", "The sequence threshold is calibrated from baseline data only, avoiding test-set threshold leakage. In the implementation, $\\alpha=0.90$ and the update uses the continuous composite threat score $S_{\\mathrm{comp},k}$ rather than a binary detector flag."),
    ("\\subsection{Quorum Fusion}\n", "\\subsection{Continuous Composite Threat Score}\nThe three detector streams are also mapped to a bounded continuous score. With normalized component scores $S_{\\mathrm{NIS},k}$, $S_{\\mathrm{CUSUM},k}$, and $S_{\\mathrm{JITTER},k}$,\n\\begin{equation}\nS_{\\mathrm{comp},k}=w_1S_{\\mathrm{NIS},k}+w_2S_{\\mathrm{CUSUM},k}+w_3S_{\\mathrm{JITTER},k},\\qquad \\sum_i w_i=1,\n\\end{equation}\nwhere the implementation uses $(w_1,w_2,w_3)=(0.50,0.30,0.20)$ and clips each component and the final score to $[0,1]$.\n\n\\subsection{Quorum Fusion}\n"),
    ("../results/independent_validation_run/paper_figures/", "../results/authoritative_validation_20260815/paper_figures/"),
]


def main():
    text = PAPER.read_text(encoding="utf-8")
    changed = False
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new); changed = True
        elif new not in text:
            raise SystemExit(f"PATCH FAILURE: expected manuscript text not found: {old[:90]!r}")
    if changed:
        PAPER.write_text(text, encoding="utf-8")
        print("Applied audited manuscript/code consistency corrections")
    else:
        print("Manuscript consistency corrections already applied")

if __name__ == "__main__":
    main()
