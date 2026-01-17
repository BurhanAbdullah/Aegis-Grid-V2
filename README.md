# Aegis-Grid V2.0: Agentic Security for Intelligent Power Systems

## Project Overview
Aegis-Grid V2.0 is a proprietary framework for high-assurance grid communication. It addresses the "Harvest Now, Decrypt Later" threat through a combination of Post-Quantum (PQ) identity roots and autonomous agent-mediated resilience.

## Technical Architecture (7-Layer Stack)
The system operates on an integrated stack where each layer informs the next:

1. **Hardware Identity**: MAC-ID pinning bound to the Lattice-Root.
2. **Temporal Safety**: Strict 2.0s jitter monitoring to detect injection.
3. **Adaptive Quorum**: Agent-based (n, k) thresholding.
4. **Shannon Stealth**: Positional shuffling within high-entropy bursts.
5. **Pressure Analysis**: Cumulative Attack Pressure (CAP) monitoring.
6. **Fail-Secure**: Autonomous data-locking upon boundary breach.
7. **Vault Isolation**: Physical and logical separation of V2 logic.

## Management via Bash
The system is managed through the central `manage.sh` controller.
- **Initialization**: Run `./manage.sh setup` to prepare the environment.
- **Verification**: Run `./manage.sh audit` to execute the full-scale simulation.
- **Forensics**: Logs are stored in `v2_model/logs/` and visual metrics in `v2_model/plots/`.

---
© 2026 Burhan Abdullah. Proprietary Research. Unauthorized distribution prohibited.
