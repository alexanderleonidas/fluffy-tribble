import random
import math
from tva.enums import VotingScheme, HappinessFunc

class Voter:
    def __init__(self, voter_id, candidates, seed=None):
        self.voter_id = voter_id
        self.rng = random.Random(seed)
        self.preferences: list[str] = self.get_preferences(candidates)

    def get_preferences(self, c:list[str]) -> list[str]:
        # Shuffles the candidate list using random.Random with a seed
        indices = list(range(len(c)))
        self.rng.shuffle(indices)
        return [c[i] for i in indices]

    def __repr__(self):
        return f'Voter {self.voter_id}: {self.preferences}'

    # ------------------------------
    # Scheme-specific happiness functions
    # ------------------------------