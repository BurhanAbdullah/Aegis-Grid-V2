class PredictiveRiskContainment:
    def governance_weight(self, trust, predicted_risk):
        return trust * (1.0 - predicted_risk)
