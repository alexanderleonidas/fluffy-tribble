from globals import *
from random import randint, sample


class Strategies:
    def __init__(self, preference_matrix):
        self.preference_matrix = preference_matrix
        self.num_strategic = NUM_STRATEGIC_VOTERS
        self.strategic_voter_ids = sample(range(0, len(self.preference_matrix)), self.num_strategic)

    def compromising(self):
        """ A voter ranks an alternative insincerely higher than another """
        # strategic_preference_matrix = []
        for voter in self.preference_matrix:
            if voter.id in self.strategic_voter_ids:
                # Swap the first and second preference in the list
                voter.preferences[0], voter.preferences[1] = voter.preferences[1], voter.preferences[0]


    def burying(self):
        """ A voter ranks an alternative insincerely lower than another """
        for voter in self.preference_matrix:
            if voter.id in self.strategic_voter_ids:
                # Swap the penultimate and last preference in the list
                voter.preferences[-2], voter.preferences[-1] = voter.preferences[-1], voter.preferences[-2]