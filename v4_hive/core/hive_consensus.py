from collections import deque

class ProtectorAgent:
    def __init__(self, nis_threshold=13.277, state_tol=0.05):
        self.nis_threshold = nis_threshold
        self.state_tol = state_tol
    def vote(self, nis, state_dev):
        return int(nis > self.nis_threshold or state_dev > self.state_tol)

class AuditorAgent:
    def __init__(self, hamming_threshold=1):
        self.hamming_threshold = hamming_threshold
    def vote(self, timing_det, brk_hamming):
        return int(timing_det or brk_hamming > self.hamming_threshold)

class MonitorAgent:
    def __init__(self, cusum_threshold=5.0, entropy_min=2.0):
        self.cusum_threshold = cusum_threshold
        self.entropy_min = entropy_min
    def vote(self, cusum_stat, traffic_ent, pf_diverged):
        return int(cusum_stat > self.cusum_threshold
                   or traffic_ent < self.entropy_min or pf_diverged)

class HiveConsensus:
    def __init__(self, persistence=3, alpha=0.9, theta_max=10.0):
        self.protector = ProtectorAgent()
        self.auditor = AuditorAgent()
        self.monitor = MonitorAgent()
        self.history = deque(maxlen=persistence)
        self.persistence = persistence
        self.threat_score = 0.0
        self.alpha = alpha
        self.theta_max = theta_max

    def step(self, nis, state_dev, timing_det, brk_hamming,
             cusum_stat, traffic_ent, pf_diverged):
        v_p = self.protector.vote(nis, state_dev)
        v_a = self.auditor.vote(timing_det, brk_hamming)
        v_m = self.monitor.vote(cusum_stat, traffic_ent, pf_diverged)
        consensus = int((v_p + v_a + v_m) >= 2)
        self.history.append(consensus)
        self.threat_score = self.alpha * self.threat_score + consensus
        persistent = int(sum(self.history) >= self.persistence)
        level = min(3, int((self.threat_score/self.theta_max)*3)+1) if persistent else 0
        return {"v_p":v_p,"v_a":v_a,"v_m":v_m,"consensus":consensus,
                "mitigation":persistent,"level":level,
                "threat_score":round(self.threat_score,3)}
