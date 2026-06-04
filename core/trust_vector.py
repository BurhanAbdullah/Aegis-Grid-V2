class TrustVector:
    def __init__(self):
        self.competence = 1.0
        self.behavior = 1.0
        self.loyalty = 1.0
        self.stability = 1.0

    def aggregate(self):
        return (
            self.competence +
            self.behavior +
            self.loyalty +
            self.stability
        ) / 4.0
