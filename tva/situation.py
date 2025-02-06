import random
import string
from tva.globals import *
from tva.voter import Voter
import numpy as np

class Situation:
    def __init__(self, num_voters, num_candidates, seed=None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.candidates = self.__create_candidates(num_candidates)
        self.voters, self.preference_matrix = self.__create_situation(num_voters)

    def __create_situation(self, num_voters=4):
        """ Creates a preference matrix """
        voters = []
        preference_matrix = []
        for i in range(num_voters):
            voter_seed = self.rng.randint(0, 2**32 - 1)
            voter = Voter(i, self.candidates, seed=voter_seed)
            voters.append(voter)
            preference_matrix.append(voter.preferences)

        return voters, preference_matrix

    def average_happiness(self, winner):
        """ Calculate the average happiness of all voters. """
        return np.mean([voter.happiness(winner) for voter in self.voters])

    @staticmethod
    def __create_candidates(num_candidates=4):
        """Return a list of the first `n` uppercase letters of the alphabet."""
        n = min(max(num_candidates, 0), 26)  # Ensure n is between 0 and 26
        return list(string.ascii_uppercase[:n])
    
    def __repr__(self) -> str:
        return f'Situation: {self.voters}'
