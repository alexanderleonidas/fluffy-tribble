import math
from tva.enums import Happiness

class HappinessCounter:

    def calculate_happiness(self, winner:str, happiness_type:Happiness):
        """ Apply the specified voting scheme to determine the winner. """
        if happiness_type == Happiness.:
            return self.__plurality_happiness(winner)
        elif happiness_type == Happiness.:
            return self.__voting_for_two_happiness(winner)
        elif happiness_type == Happiness.:
            return self.__anti_plurality_happiness(winner)
        elif happiness_type == Happiness.:
            return self.__borda_happiness(winner)
    
    def __plurality_happiness(self, winner:str):
        """
        For plurality voting use a logarithmic decay.
        If the winning candidate is ranked r (1-indexed),
          H_i = 1 / log2(r + 1)
        so that a voter whose top candidate wins (r = 1) gets happiness 1.
        """
        r = self.preferences.index(winner) + 1  # convert to 1-index
        return 1 / math.log2(r + 1)

    def __anti_plurality_happiness(self, winner:str, decay_alpha=0.5):
        """
        For anti-plurality voting use an exponential decay.
        Here we use a “shift” so that if the winner is a voter's top choice (r = 1),
          H_i = exp(-alpha*(1-1)) = exp(0) = 1.
        For lower-ranked outcomes, happiness decays as:
          H_i = exp(-alpha*(r-1))
        """
        r = self.preferences.index(winner) + 1
        return math.exp(-decay_alpha * (r - 1))

    def __voting_for_two_happiness(self, winner:str):
        """
        For voting-for-two, assign:
          0.7 if winner is top choice,
          0.3 if winner is second,
          0.0 otherwise.
        """
        if self.preferences[0] == winner:
            return 0.7
        elif len(self.preferences) > 1 and self.preferences[1] == winner:
            return 0.3
        else:
            return 0.0

    def __borda_happiness(self, winner:str):
        """
        For Borda voting, we use a normalized linear score.
        If there are m candidates and the winner is at rank r (1-indexed),
          H_i = (m - r) / (m - 1)
        so that a top-ranked candidate gives H_i = 1 and the last-ranked gives H_i = 0.
        """
        c = len(self.preferences) # Number of candidates
        r = self.preferences.index(winner) + 1
        return  (c - r) / (c - 1) if c > 1 else 1.0
    
    # What 4 names can we give to these functions?
    