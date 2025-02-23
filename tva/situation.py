import random
import string
from tva.voter import Voter
import numpy as np
from tva.enums import VotingScheme, Happiness


class Situation:
    def __init__(self, num_voters, num_candidates, seed=None, candidates=None, voters=None):
        assert num_candidates > 0, "Number of candidates must be greater than 0."
        assert num_candidates < 10, "If the number of candidates is greater than 9, there are too many permutations to calculate quickly."
        if seed is not None:
            # Generate a random seed if none is provided
            self.seed = random.randint(0, 2**32 - 1)
        else:
            self.seed = seed
        self.rng = random.Random(seed)
        if candidates is None:
            self.candidates = self.__create_candidates(num_candidates)
        else:
            self.candidates = candidates
        if voters is None:
            self.voters:list[Voter] = self.__create_situation(num_voters)
        else:
            if all(isinstance(v, list) for v in voters):
                self.voters = []
                for i, pref in enumerate(voters):
                    voter = Voter(i, self.candidates)
                    voter.preferences = pref
                    self.voters.append(voter)

    def __create_situation(self, num_voters=4) -> list[Voter]:
        """ Creates a preference matrix """
        voters = []
        for i in range(num_voters):
            voter_seed = self.rng.randint(0, 2**32 - 1)
            voter = Voter(i, self.candidates, seed=voter_seed)
            voters.append(voter)

        return voters

    def average_happiness(self, winner, happiness_func:Happiness):
        """ Calculate the total happiness of all voters. """
        return np.sum([voter.calculate_happiness(winner, happiness_func) for voter in self.voters])

    @staticmethod
    def __create_candidates(num_candidates=4):
        """Return a list of the first `n` uppercase letters of the alphabet."""
        n = min(max(num_candidates, 0), 26)  # Ensure n is between 0 and 26
        return list(string.ascii_uppercase[:n])
    
    def __repr__(self) -> str:
        message = ""
        for voter in self.voters:
            message += str(voter) + "\n"
        return message
