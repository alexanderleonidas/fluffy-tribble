import string
from globals import *
from voter import Voter
from schemes import Schemes
from strategies import Strategies

class Situation:
    def __init__(self):
        self.candidates = self.create_candidates(NUM_CANDIDATES)
        self.preference_matrix = self.create_situation(NUM_VOTERS)
        self.schemes = Schemes(self.preference_matrix)
        self.strategies = Strategies(self.preference_matrix)

    def get_happiness(self):
        pass


    def create_situation(self, num_voters=4):
        """ Creates a preference matrix """
        preference_matrix = []
        for i in range(num_voters):
            voter = Voter(i, self.candidates)
            preference_matrix.append(voter)
        return preference_matrix


    @staticmethod
    def create_candidates(num_candidates):
        """Return a list of the first `n` uppercase letters of the alphabet."""
        n = min(max(num_candidates, 0), 26)  # Ensure n is between 0 and 26
        return list(string.ascii_uppercase[:n])


    def print_preference_matrix(self):
        # Extract voter IDs
        voter_ids = [f"V{voter.id}" for voter in self.preference_matrix]

        # Convert Voter objects to lists of preferences
        matrix = [voter.preferences for voter in self.preference_matrix]

        # Transpose the matrix to print column-wise
        transposed = list(zip(*matrix))

        # Print the header with voter IDs
        print("Preference matrix:")
        print(f"{'        '} {' '.join(voter_ids)}")

        # Print the matrix in a clean format
        for i, row in enumerate(transposed):
            print(f"Rank {i + 1}   {'  '.join(row)}")

