import random
import numpy as np
from enum import Enum

class Voter:
    def __init__(self, voter_id, candidates, seed=None):
        self.voter_id = voter_id
        self.rng = random.Random(seed)
        self.preferences = self.get_preferences(candidates)

    def get_preferences(self, c):
        # Shuffles the candidate list using random.Random with a seed
        indices = list(range(len(c)))
        self.rng.shuffle(indices)
        return [c[i] for i in indices]

    def __repr__(self):
        return f'Voter {self.voter_id}: {self.preferences}'

    def happiness(self, winner):
        """
        Happiness = How highly the winning candidate was ranked by the voter.
        If a voter ranked the winner 1st, they are maximally happy.
        If they ranked them last, they are completely unhappy.
        """
        return 1 - ((self.preferences.index(winner))/(len(self.preferences)-1))
    