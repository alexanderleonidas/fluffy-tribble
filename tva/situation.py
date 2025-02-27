import random
import string
from tva.voter import Voter


class Situation:
    def __init__(self, num_voters, num_candidates, seed=None, candidates=None, voters=None, info=None):
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
        if info is not None:
            for voter in self.voters:
                new_preferences = []
                for candidate in voter.preferences:
                    if self.rng.random() < info:
                        new_preferences.append("?")
                    else:
                        new_preferences.append(candidate)
                voter.preferences = new_preferences

    def __create_situation(self, num_voters=4) -> list[Voter]:
        """ Creates a preference matrix """
        voters = []
        for i in range(num_voters):
            voter_seed = self.rng.randint(0, 2**32 - 1)
            voter = Voter(i, self.candidates, seed=voter_seed)
            voters.append(voter)

        return voters

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

    def print_preference_matrix(self):
        # Extract voter IDs
        voter_ids = [f"V{voter.voter_id}" for voter in self.voters]

        # Convert Voter objects to lists of preferences
        matrix = [voter.preferences for voter in self.voters]

        # Transpose the matrix to print column-wise
        transposed = list(zip(*matrix))

        # Print the header with voter IDs
        print("Preference matrix:")
        print(f"{'        '} {' '.join(voter_ids)}")

        # Print the matrix in a clean format
        for i, row in enumerate(transposed):
            print(f"Rank {i + 1}   {'  '.join(row)}")