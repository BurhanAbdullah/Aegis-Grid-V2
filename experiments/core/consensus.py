class ConsensusFusion:
    def step(self, kalman, cusum, jitter):
        votes = int(kalman) + int(cusum) + int(jitter)

        return {
            "votes": votes,
            "consensus": votes >= 2,
            "mitigation": votes >= 2
        }
