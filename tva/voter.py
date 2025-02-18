import random
import math
from tva.enums import VotingScheme, Happiness

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
    
    def calculate_happiness(self, winner:str, happiness_func:Happiness):
        """ Apply the specified voting scheme to determine the winner. """
        if happiness_func == Happiness.LOG:
            return self.__logarithmic_happiness(winner)
        elif happiness_func == Happiness.EXP:
            return self.__exponential_happiness(winner)
        elif happiness_func == Happiness.LINEAR:
            return self.__linear_happiness(winner)
    
    def __logarithmic_happiness(self, winner:str):
        """
        A logarithmic decay hapiness function.
        If the winning candidate is ranked r (1-indexed),
          H_i = 1 / log2(r + 1)
        so that a voter whose top candidate wins (r = 1) gets happiness 1.
        """
        r = self.preferences.index(winner) + 1  # convert to 1-index
        return 1 / math.log2(r + 1)

    def __exponential_happiness(self, winner:str, decay_alpha=0.5):
        """
        An exponential decay happiness function.
        Here we use a “shift” so that if the winner is a voter's top choice (r = 1),
          H_i = exp(-alpha*(1-1)) = exp(0) = 1.
        For lower-ranked outcomes, happiness decays as:
          H_i = exp(-alpha*(r-1))
        """
        r = self.preferences.index(winner) + 1
        return math.exp(-decay_alpha * (r - 1))

    def __linear_happiness(self, winner:str):
        """
        A normalized linear score happiness function.
        If there are m candidates and the winner is at rank r (1-indexed),
          H_i = (m - r) / (m - 1)
        so that a top-ranked candidate gives H_i = 1 and the last-ranked gives H_i = 0.
        """
        c = len(self.preferences) # Number of candidates
        r = self.preferences.index(winner) + 1
        return  (c - r) / (c - 1) if c > 1 else 1.0