# XMON-Grid Authoritative Model Implementation Audit

**Date**: 2026-08-11  
**Repository Branch**: `tsg-clean-reproduction`  
**Commit**: `395d4cf1ab22f4061f49de23fa9b1e4c48407df2`  
**Status**: **READY FOR EVALUATION**

---

## 1. CANONICAL MODEL EQUATIONS (`core/xmon_model.py`)

The single authoritative model implementation for XMON-Grid is contained in [`core/xmon_model.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/core/xmon_model.py). All active experiments import from this module.

### 1.1 State Vector & Measurement Model
For a power grid with $N$ buses:
* **State Vector**: $\mathbf{x}_k = [\theta_2, \dots, \theta_N, V_1, \dots, V_N]^T \in \mathbb{R}^{2N-1}$ (where $\theta_1 = 0$ is the reference bus angle).
* **Measurement Vector**: $\mathbf{z}_k = [\mathbf{V}^T, \mathbf{P}^T, \mathbf{Q}^T]^T \in \mathbb{R}^{3N}$ consisting of voltage magnitudes, active power injections, and reactive power injections.
* **Measurement Function**: $\mathbf{h}(\mathbf{x}) = [\mathbf{V}^T, \mathbf{P}(\mathbf{x})^T, \mathbf{Q}(\mathbf{x})^T]^T$ where:
  $$P_i(\mathbf{x}) = \sum_{j=1}^N V_i V_j \left( G_{ij} \cos(\theta_i - \theta_j) + B_{ij} \sin(\theta_i - \theta_j) \right)$$
  $$Q_i(\mathbf{x}) = \sum_{j=1}^N V_i V_j \left( G_{ij} \sin(\theta_i - \theta_j) - B_{ij} \cos(\theta_i - \theta_j) \right)$$
* **Measurement Jacobian**: $\mathbf{H}_k = \frac{\partial \mathbf{h}(\mathbf{x})}{\partial \mathbf{x}} \in \mathbb{R}^{3N \times (2N-1)}$ computed analytically via bus admittance matrix $\mathbf{Y}_{\text{bus}} = \mathbf{G} + j\mathbf{B}$.

### 1.2 State Estimation & NIS
* **State Prediction**: $\hat{\mathbf{x}}_{k|k-1} = \hat{\mathbf{x}}_{k-1|k-1}$, $\mathbf{P}_{k|k-1} = \mathbf{P}_{k-1|k-1} + \mathbf{Q}$.
* **Measurement Residual / Innovation**: $\mathbf{r}_k = \mathbf{z}_k - \mathbf{h}(\hat{\mathbf{x}}_{k|k-1}) \in \mathbb{R}^{3N}$.
* **Innovation Covariance**: $\mathbf{S}_k = \mathbf{H}_k \mathbf{P}_{k|k-1} \mathbf{H}_k^T + \mathbf{R} \in \mathbb{R}^{3N \times 3N}$.
* **Normalized Innovation Squared (NIS)**:
  $$\text{NIS}_k = \mathbf{r}_k^T \mathbf{S}_k^{-1} \mathbf{r}_k$$
  *(Computed numerically via `np.linalg.solve(S_k, r_k)` without explicit matrix inversion).*
* **State Update (Joseph Form)**:
  $$\mathbf{K}_k = \mathbf{P}_{k|k-1} \mathbf{H}_k^T \mathbf{S}_k^{-1}$$
  $$\hat{\mathbf{x}}_{k|k} = \hat{\mathbf{x}}_{k|k-1} + \mathbf{K}_k \mathbf{r}_k$$
  $$\mathbf{P}_{k|k} = (\mathbf{I} - \mathbf{K}_k \mathbf{H}_k) \mathbf{P}_{k|k-1} (\mathbf{I} - \mathbf{K}_k \mathbf{H}_k)^T + \mathbf{K}_k \mathbf{R} \mathbf{K}_k^T$$

### 1.3 Individual Detectors
1. **NIS Detector**:
   $$A_{\text{NIS}} = \mathbb{I}(\text{NIS}_k > \gamma_{\text{NIS}})$$
   where $\gamma_{\text{NIS}} = \chi^2_{3N, 1-\alpha}$ at significance level $\alpha = 0.01$.
2. **One-Sided CUSUM Detector**:
   $$y_k = \frac{\text{NIS}_k - \mu_{\text{NIS}, 0}}{\sigma_{\text{NIS}, 0}}, \quad g_k = \max(0.0, g_{k-1} + y_k - \mu_0 - \kappa)$$
   $$A_{\text{CUSUM}} = \mathbb{I}(g_k > h_{\text{CUSUM}})$$
   with $\mu_0 = 0.0, \kappa = 0.5, h_{\text{CUSUM}} = 5.0$.
3. **Communication Jitter Detector**:
   $$J_k = \frac{|\Delta t_k - \mu_T|}{\sigma_T}, \quad \bar{J}_W(k) = \frac{1}{W} \sum_{i=0}^{W-1} J_{k-i}$$
   $$A_{\text{Jitter}} = \mathbb{I}\left(J_k > \eta_\sigma \land \bar{J}_W(k) > \eta_\mu\right)$$
   with nominal $\mu_T = 0.004$ s ($4$ ms), $\sigma_T = 0.0005$ s ($0.5$ ms), $\eta_\sigma = 3.5, \eta_\mu = 2.0, W = 20$.

### 1.4 Continuous Composite Threat Score & Sequential Accumulator
* **Normalized Components**:
  $$S_{\text{NIS}} = \min\left(1.0, \frac{\max(0, \text{NIS}_k)}{2 \gamma_{\text{NIS}}}\right), \quad S_{\text{CUSUM}} = \min\left(1.0, \frac{g_k}{2 h_{\text{CUSUM}}}\right), \quad S_{\text{Jitter}} = \min\left(1.0, \frac{\bar{J}_W(k)}{2 \eta_\mu}\right)$$
* **Composite Continuous Threat Score**:
  $$S_{\text{comp}}(k) = 0.50 S_{\text{NIS}} + 0.30 S_{\text{CUSUM}} + 0.20 S_{\text{Jitter}} \in [0.0, 1.0]$$
  *(Note: Discrete consensus vote $V_{\text{consensus}}$ is strictly excluded).*
* **Sequential Accumulator**:
  $$\Theta_k = 0.90 \Theta_{k-1} + S_{\text{comp}}(k), \quad A_{\text{seq}} = \mathbb{I}(\Theta_k > \tau_{\text{seq}})$$
  where $\tau_{\text{seq}} = \mu_{\Theta, \text{benign}} + 3 \sigma_{\Theta, \text{benign}}$ estimated strictly from benign calibration data.

### 1.5 Quorum Voting Logic
* **Vote Sum**: $V = A_{\text{NIS}} + A_{\text{CUSUM}} + A_{\text{Jitter}} \in \{0, 1, 2, 3\}$.
* **Strict Majority Quorum ($K=2$)**: $D_{K=2} = \mathbb{I}(V \ge 2)$.
* **Sensitivity Mode ($K=1$)**: $D_{K=1} = \mathbb{I}(V \ge 1)$.

---

## 2. PARAMETERS & DIMENSIONS BY TEST CASE

| Test Case | Buses ($N$) | State Dim ($2N-1$) | Meas Dim ($3N$) | Chi-Square Threshold ($\gamma_{\text{NIS}}, \alpha=0.01$) | $\sigma_V$ (p.u.) | $\sigma_P, \sigma_Q$ (p.u.) | Nominal IAT ($\mu_T$) |
|---|---|---|---|---|---|---|---|
| **case9** | 9 | 17 | 27 | 46.96 | 0.002 | 0.005 | 0.004 s (4 ms) |
| **case14** | 14 | 27 | 42 | 66.21 | 0.002 | 0.005 | 0.004 s (4 ms) |
| **case30** | 30 | 59 | 90 | 124.12 | 0.002 | 0.005 | 0.004 s (4 ms) |
| **case118** | 118 | 235 | 354 | 422.37 | 0.002 | 0.005 | 0.004 s (4 ms) |

---

## 3. CALIBRATION & DATA SPLIT METHODOLOGY

1. **Calibration Split (BENIGN ONLY)**:
   * 200 nominal benign SCADA cycles per test case.
   * Used **strictly** to calibrate $\mu_{\text{NIS}, 0}, \sigma_{\text{NIS}, 0}, \mu_T, \sigma_T$, and $\tau_{\text{seq}} = \mu_{\Theta, \text{benign}} + 3 \sigma_{\Theta, \text{benign}}$.
   * **Zero attack data enters calibration** (100% data leakage prevention).
2. **Validation Split**:
   * 100 SCADA cycles per case (50% benign, 50% mild attacks) used to confirm hyperparameter stability.
3. **Test Split**:
   * 240 SCADA cycles per case (60 samples $\times$ 4 scenarios: `baseline`, `branch_outage`, `fdia`, `stealth_drift`).
   * Completely untouched during calibration.

---

## 4. NUMERICAL STABILITY CHECKS

1. **Covariance Symmetry**: Enforced after every state update via $\mathbf{S}_k = \frac{1}{2}(\mathbf{S}_k + \mathbf{S}_k^T)$ and $\mathbf{P}_{k|k} = \frac{1}{2}(\mathbf{P}_{k|k} + \mathbf{P}_{k|k}^T)$.
2. **Conditioning & Ridge Regularization**: If $\text{cond}(\mathbf{S}_k) > 10^{12}$, diagonal regularization $\mathbf{S}_k \leftarrow \mathbf{S}_k + 10^{-6} \mathbf{I}$ is automatically applied.
3. **Matrix Inversion Safety**: Uses `np.linalg.solve(S_k, r_k)` rather than `inv(S_k)`.
4. **Joseph Form Covariance Update**: Guarantees positive-definiteness of $\mathbf{P}_{k|k}$ across all iterations.

---

## 5. REPOSITORY CODE CLASSIFICATION

| File Path | Status | Role |
|---|---|---|
| [`core/xmon_model.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/core/xmon_model.py) | **ACTIVE (CANONICAL)** | Single authoritative EKF, NIS, CUSUM, Jitter, Composite Threat Score, and Quorum Voting model. |
| [`core/grid_topology.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/core/grid_topology.py) | **ACTIVE (CANONICAL)** | IEEE test case topologies, bus admittance matrices $\mathbf{Y}_{\text{bus}}$, measurement function $\mathbf{h}(\mathbf{x})$, and analytical Jacobians $\mathbf{H}(\mathbf{x})$. |
| [`core/data_pipeline.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/core/data_pipeline.py) | **ACTIVE (CANONICAL)** | Physical AC power flow measurement generator, attack injection models, and clean calibration/val/test splits. |
| [`tests/test_xmon_model.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/tests/test_xmon_model.py) | **ACTIVE (CANONICAL)** | Unit test suite covering items A through K. |
| [`experiments/sequential_detector.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/experiments/sequential_detector.py) | **LEGACY** | Preserved for historical reference. |
| [`experiments/fusion_detector.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/experiments/fusion_detector.py) | **LEGACY** | Preserved for historical reference. |
| [`experiments/run_full_macpr_experiment.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/experiments/run_full_macpr_experiment.py) | **LEGACY** | Preserved for historical reference. |
| [`scripts/generate_realistic_dataset.py`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/scripts/generate_realistic_dataset.py) | **ARCHIVAL** | Synthetic random generator (superseded by physical data pipeline). |

---

## 6. UNIT TEST SUITE RESULTS (`tests/test_xmon_model.py`)

```text
python -m unittest discover -s tests -p "test_*.py"
...........
----------------------------------------------------------------------
Ran 11 tests in 0.242s

OK
```

### Test Coverage Summary:
* **Test A (State Estimator Dimensions)**: PASSED ($2N-1$ state, $3N$ measurement).
* **Test B (Innovation Dimensions)**: PASSED ($\mathbf{r}_k \in \mathbb{R}^{3N}$).
* **Test C (Covariance S Positive Definiteness & Symmetry)**: PASSED (all eigenvalues $> 0$, symmetric).
* **Test D (NIS Non-Negativity)**: PASSED ($\text{NIS}_k \ge 0.0$).
* **Test E (NIS Nominal Distribution)**: PASSED (E[NIS] bounded under benign noise).
* **Test F (CUSUM Reset Behavior)**: PASSED (resets accumulator to $0.0$).
* **Test G (Jitter Calculation & Windowing)**: PASSED (correct z-scores and dual-threshold triggering).
* **Test H (Composite Score Range)**: PASSED ($S_{\text{comp}} \in [0.0, 1.0]$).
* **Test I (Quorum K=2 Strict Majority Logic)**: PASSED ($D_{K=2} = 1 \iff V \ge 2$).
* **Test J (Quorum K=1 Sensitivity Logic)**: PASSED ($D_{K=1} = 1 \iff V \ge 1$).
* **Test K (Deterministic Reproduction)**: PASSED (identical output for fixed seed).

---

## 7. REMAINING LIMITATIONS & SCOPE BOUNDARIES

1. **Power System Equations**: The implementation covers AC power flow equations and measurement Jacobians $\mathbf{H}(\mathbf{x})$ for IEEE 9, 14, 30, and 118 bus cases.
2. **Frequency Dynamics**: Current model assumes constant nominal system frequency ($50/60$ Hz) and focuses on voltage magnitudes, phase angles, power flows, and communication timing jitter.

---

## 8. MODEL STATUS

**MODEL STATUS = READY**
