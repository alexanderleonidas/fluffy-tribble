from collections import Counter, defaultdict
from tva.globals import *
from enum import Enum

# Create an enum with every type of voting
class VotingScheme(Enum):
    PLURALITY = 1
    VOTE_FOR_TWO = 2
    ANTI_PLURALITY = 3


class Schemes:
    def apply_voting_scheme(self, voting_scheme, preference_matrix):
        """ Apply the specified voting scheme to determine the winner. """
        if voting_scheme == VotingScheme.PLURALITY:
            return self.plurality_voting(preference_matrix)
        elif voting_scheme == VotingScheme.VOTE_FOR_TWO:
            return self.voting_for_two(preference_matrix)
        elif voting_scheme == VotingScheme.ANTI_PLURALITY:
            return self.anti_plurality_voting(preference_matrix)
        else:
            raise ValueError('Invalid voting scheme')
    
    def plurality_voting(self, preference_matrix):
        """ Apply plurality voting to determine the winner. """
        # Get first-choice votes
        first_choices = [preferences[0] for preferences in preference_matrix]
        # Count occurrences of each candidate
        vote_counts = Counter(first_choices)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get) # type: ignore
        return winner

    def __voting_for_n(self, n, preference_matrix):
        # Get top n choices
        top_n_choices = [preferences[:n] for preferences in preference_matrix]
        # Flatten list
        all_votes = [candidate for pair in top_n_choices for candidate in pair]
        # Count occurrences of each candidate
        vote_counts = Counter(all_votes)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get) # type: ignore
        return winner
        

    def voting_for_two(self, preference_matrix):
        """ Apply vote-for-two voting to determine the winner. """
        return self.__voting_for_n(2, preference_matrix)

    def anti_plurality_voting(self, preference_matrix):
        """ Apply anti-plurality voting to determine the winner. """
        # Exclude last choice
        return self.__voting_for_n(-1, preference_matrix)


    def borda_voting(self, preference_matrix):
        """ Apply Borda count voting to determine the winner. """
        # Get total number of candidates
        num_candidates = len(preference_matrix[0])
        # Dictionary to store candidate scores
        scores = defaultdict(int)
        for preferences in preference_matrix:
            for rank, candidate in enumerate(preferences):
                # Assign points
                scores[candidate] += (num_candidates - 1 - rank)
        # Candidate with most points
        winner = max(scores, key=scores.get) # type: ignore
        return winner