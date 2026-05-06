<p align="center">
  <img src="Banner.png" width="100%" alt="XMON-Grid Banner"/>
</p>

# XMON-Grid

## Sequential Residual Accumulation and Multi-Agent Consensus for Cross-Layer Cyber–Physical Anomaly Detection in IEEE Benchmark Power Systems

Implementation and reproducible evaluation framework accompanying the paper:

> **Sequential Innovation and Cross-Layer Consensus Monitoring for Coordinated Topology and Timing Attack Detection in Smart Grids**

---

# Overview

XMON-Grid implements a reproducible multi-agent cyber–physical monitoring framework for coordinated topology manipulation, timing anomalies, and cross-layer attack detection in SCADA-monitored transmission systems.

The framework integrates:

- Sequential innovation accumulation
- Adaptive Page–Hinkley CUSUM monitoring
- Cross-layer anomaly fusion
- Jacobian conditioning analysis
- Timing-jitter anomaly statistics
- Distributed multi-agent coordination
- Authenticated consensus-guided mitigation
- MATPOWER AC power-flow validation

across IEEE benchmark transmission networks including:
- IEEE 9-bus
- IEEE 14-bus
- IEEE 30-bus
- IEEE 57-bus
- IEEE 118-bus
- IEEE 300-bus

---

# Multi-Agent Architecture

The framework evaluates coordinated monitoring using distributed agents:

| Agent | Function |
|---|---|
| Monitor Agent | Timing and communication anomaly monitoring |
| Auditor Agent | Sequential physics residual analysis |
| Protector Agent | Consensus-triggered mitigation coordination |
| Coordinator Agent | Multi-agent authenticated vote fusion |

The implementation evaluates:
- distributed evidence fusion,
- sequential residual accumulation,
- adaptive thresholding,
- and consensus-triggered mitigation behavior.

---

# Core Detection Components

## Sequential Physics Accumulator

The implemented sequential accumulator follows:

\[
\Theta(k)=0.9\Theta(k-1)+NIS(k)
\]

with adaptive threshold calibration:

\[
\text{threshold} = \mu + 0.5\sigma
\]

where:
- \(\mu = 211.8084\)
- \(\sigma = 58.5532\)

This enables:
- persistence-sensitive anomaly accumulation,
- weak-signal temporal aggregation,
- and low-amplitude residual monitoring.

---

## Communication-Layer Monitoring

The communication layer evaluates:
- timing jitter statistics,
- Page–Hinkley sequential monitoring,
- consensus activation behavior,
- and coordinated anomaly propagation.

---

## Consensus-Guided Mitigation

The framework evaluates authenticated multi-agent consensus under crash-fault-tolerant coordination assumptions.

Observed runtime behavior:

| Scenario | Consensus | Mitigation |
|---|---|---|
| Baseline | 0 | False |
| Stealth | 0 | False |
| Flood | 1 | True |
| Timing | 1 | True |

The current implementation demonstrates:
- strong communication-layer sensitivity,
- layered corroboration,
- and sequential residual support for persistent anomalies.

---

# Repository Structure

```text
paper/              Manuscript sources, figures, and tables
paper/data/         Reproducible exported CSV artifacts
paper/figures/      Generated paper figures
scripts/            Experiment and evaluation scripts
experiments/        Monte Carlo and stealth evaluations
agents/             Multi-agent coordination modules
core/               Consensus and mitigation logic
matpower/           MATPOWER AC power-flow validation
results/            Runtime detector outputs
plotting_data/      CSV traces used for plotting
validation/         Reproducibility verification scripts
