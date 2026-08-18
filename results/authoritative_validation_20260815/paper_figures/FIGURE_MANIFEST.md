# Authoritative publication figure manifest

```json
{
  "detector_rows": 1200,
  "figure_design": {
    "annotation_policy": "no overlapping data labels; no rotated scientific-notation bar labels",
    "format": "PDF + 400 dpi PNG",
    "legend_policy": "outside data region where practical",
    "scientific_values_changed": false,
    "titles_inside_axes": false,
    "uncertainty": "authoritative CSV CI/SD"
  },
  "k1_primary": {
    "F1": 0.9238187078109933,
    "FN": 2,
    "FP": 156,
    "FPR": 0.65,
    "Precision": 0.8599640933572711,
    "Recall": 0.9979166666666667,
    "TN": 84,
    "TP": 958
  },
  "k2_five_seed": {
    "F1_mean": 0.9203815083074577,
    "F1_sd": 0.002555934330891828,
    "FPR_mean": 0.1525,
    "FPR_sd": 0.019676198255195988,
    "Recall_mean": 0.885,
    "Recall_sd": 0.0011876827344782742
  },
  "negative_samples": 240,
  "positive_samples": 960,
  "pr_auc_primary": 0.9837871731102182,
  "retained_figures": [
    "fig1_overall_performance.pdf",
    "fig2_k1_vs_k2_tradeoff.pdf",
    "fig3_roc_curve.pdf",
    "fig4_pr_curve.pdf",
    "fig5_casewise_performance.pdf",
    "fig6_attackwise_performance.pdf",
    "fig10_severity_robustness.pdf",
    "fig12_ac_powerflow_consistency.pdf"
  ],
  "roc_auc_primary": 0.9574739583333333,
  "source_directory": "results/authoritative_validation_20260815"
}
```
