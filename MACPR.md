# MACPR — Multi-Signal AC Cyber-Physical Resilience

MACPR is a fused multi-layer detection pipeline integrating stochastic
monitoring, timing integrity validation, consensus arbitration, and
AC power-flow divergence detection.

## Detection Pipeline

1. AC power-flow validation via MATPOWER `runpf()` → `delta_v`
2. Kalman filter NIS statistical test → `kalman_anomaly`
3. CUSUM sequential change detector → `cusum_alarm`
4. PMU timing jitter anomaly detection → `jitter_detected`
5. Hive consensus voting across agents → `consensus`
6. Threat score fusion metric → `threat_score ∈ {0, 2.629, 4.095}`
7. Closed-loop mitigation validation → `recovery_dv`

## Tested IEEE Benchmark Systems

- IEEE 9-bus
- IEEE 14-bus
- IEEE 30-bus

## Attack Scenarios

- `branch1_out`, `branch2_out`, `branch3_out`
- Baseline false positive rate: 0% (CUSUM statistic = 0 under nominal load)

## Key Results

| Case   | Attack       | PF Success | Threat Score | Mitigation |
|--------|-------------|-----------|-------------|-----------|
| case9  | baseline    | True       | 0.0         | False     |
| case9  | branch1_out | False      | 4.095       | True      |
| case9  | branch2_out | True       | 4.095       | True      |
| case14 | baseline    | True       | 0.0         | False     |
| case14 | branch2_out | True       | 4.095       | True      |
| case30 | baseline    | True       | 0.0         | False     |
