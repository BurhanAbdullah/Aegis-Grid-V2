# MACPR — Multi-signal AC Cyber-Physical Resilience

## Detection pipeline (novel fusion)

1. AC power flow validation via MATPOWER runpf → delta_v
2. Kalman filter NIS test → kalman_anomaly  
3. CUSUM sequential detector → cusum_alarm
4. PMU timing jitter analysis → jitter_detected
5. Hive consensus voting across zones → consensus
6. Threat score fusion → threat_score ∈ {0, 2.629, 4.095}
7. Closed-loop mitigation with recovery_dv measurement

## Tested cases
- IEEE 9-bus, 14-bus, 30-bus
- Attack scenarios: branch1_out, branch2_out, branch3_out
- Baseline false positive rate: 0% (cusum_stat=0 at baseline)
