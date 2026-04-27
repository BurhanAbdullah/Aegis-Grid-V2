# MACPR — Multi-Signal AC Cyber-Physical Resilience

MACPR is a multi-layer cyber-physical detection and mitigation pipeline
integrating stochastic monitoring, timing integrity verification,
consensus arbitration, and AC power-flow stability validation.

---

## Detection Pipeline

MACPR fuses heterogeneous anomaly indicators:

1. AC power-flow validation via MATPOWER `runpf()` → ΔV
2. Kalman filter innovation test → NIS statistic
3. CUSUM sequential change detection → C⁺ statistic
4. PMU timing jitter anomaly detection → z-score
5. Hive consensus voting → majority decision
6. Threat-score fusion metric → θ
7. Closed-loop mitigation validation → recovery ΔV

---

## Mathematical Fusion Model

Threat score:

θ = w₁·NIS + w₂·C⁺ + w₃·z + w₄·ΔV

Mitigation trigger:

M = 1 if θ ≥ θ_threshold

Consensus voting rule:

M = 1 if (vP + vA + vM ≥ 2)

Persistence filter:

Σ M(k−N:k) ≥ τ

---

## Tested IEEE Benchmark Systems

- IEEE 9-bus
- IEEE 14-bus
- IEEE 30-bus

---

## Attack Scenarios

- branch1_out
- branch2_out
- branch3_out

---

## Key Results

| Case   | Attack       | PF Success | Threat Score | Mitigation |
|--------|-------------|-----------|-------------|-----------|
| case9  | baseline    | True      | 0.0         | False     |
| case9  | branch1_out | False     | 4.095       | True      |
| case9  | branch2_out | True      | 4.095       | True      |
| case14 | baseline    | True      | 0.0         | False     |
| case14 | branch2_out | True      | 4.095       | True      |
| case30 | baseline    | True      | 0.0         | False     |

Baseline false-positive rate observed:

0%
