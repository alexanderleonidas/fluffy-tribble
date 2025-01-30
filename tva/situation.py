import string
from globals import *
from tva.voter import Voter

class Situation:
    def __init__(self):
        self.candidates = self.create_candidates(NUM_CANDIDATES)
        self.voters, self.preference_matrix = self.create_situation(NUM_VOTERS)

    def create_situation(self, num_voters=4):
        """ Creates a preference matrix """
        voters = []
        preference_matrix = []
        for i in range(num_voters):
            voter = Voter(i, self.candidates)
            voters.append(voter)
            preference_matrix.append(voter.preferences)

        return voters, preference_matrix

    @staticmethod
    def create_candidates(num_candidates=4):
        """Return a list of the first `n` uppercase letters of the alphabet."""
        n = min(max(num_candidates, 0), 26)  # Ensure n is between 0 and 26
        return list(string.ascii_uppercase[:n])
