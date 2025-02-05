from collections import Counter, defaultdict
import math

class Schemes:
    def __init__(self, preference_matrix):
        self.preference_matrix = preference_matrix

    def plurality_voting(self):
        """Apply plurality voting to determine the winner."""
        # Get first-choice votes
        first_choices = [voter.preferences[0] for voter in self.preference_matrix]
        # Count occurrences of each candidate
        vote_counts = Counter(first_choices)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get)
        return winner

    def voting_for_two(self):
        """Apply vote-for-two voting to determine the winner."""
        # Get top two choices
        top_two_choices = [voter.preferences[:2] for voter in self.preference_matrix]
        # Flatten list
        all_votes = [candidate for pair in top_two_choices for candidate in pair]
        # Count occurrences of each candidate
        vote_counts = Counter(all_votes)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get)
        return winner

    def anti_plurality_voting(self):
        """Apply anti-plurality voting to determine the winner."""
        # Exclude last choice
        votes = [voter.preferences[:-1] for voter in self.preference_matrix]
        # Flatten list
        all_votes = [candidate for voter in votes for candidate in voter]
        # Count occurrences of each candidate
        vote_counts = Counter(all_votes)
        # Candidate with most points
        winner = max(vote_counts, key=vote_counts.get)
        return winner

    def borda_voting(self):
        """Apply Borda count voting to determine the winner."""
        # Get total number of candidates
        num_candidates = len(self.preference_matrix[0].preferences)
        # Dictionary to store candidate scores
        scores = defaultdict(int)
        for voter in self.preference_matrix:
            for rank, candidate in enumerate(voter.preferences):
                # Assign points (higher points for higher rank)
                scores[candidate] += (num_candidates - 1 - rank)
        # Candidate with most points
        winner = max(scores, key=scores.get)
        return winner

    # ------------------------------
    # Scheme-specific happiness functions
    # ------------------------------

    def plurality_happiness(self, winner):
        """
        For plurality voting use a logarithmic decay.
        If the winning candidate is ranked r (1-indexed),
          H_i = 1 / log2(r + 1)
        so that a voter whose top candidate wins (r = 1) gets happiness 1.
        """
        happiness = {}
        for voter in self.preference_matrix:
            r = voter.preferences.index(winner) + 1  # convert to 1-index
            h = 1 / math.log2(r + 1)
            happiness[voter.id] = h
        return happiness

    def anti_plurality_happiness(self, winner, alpha=0.5):
        """
        For anti-plurality voting use an exponential decay.
        Here we use a “shift” so that if the winner is a voter's top choice (r = 1),
          H_i = exp(-alpha*(1-1)) = exp(0) = 1.
        For lower-ranked outcomes, happiness decays as:
          H_i = exp(-alpha*(r-1))
        """
        happiness = {}
        for voter in self.preference_matrix:
            r = voter.preferences.index(winner) + 1
            h = math.exp(-alpha * (r - 1))
            happiness[voter.id] = h
        return happiness

    def voting_for_two_happiness(self, winner):
        """
        For voting-for-two, assign:
          0.7 if winner is top choice,
          0.3 if winner is second,
          0.0 otherwise.
        """
        decay=0.2
        happiness = {}
        for voter in self.preference_matrix:
            if voter.preferences[0] == winner:
                h = 0.7
            elif len(voter.preferences) > 1 and voter.preferences[1] == winner:
                h = 0.3
            else:
                h = 0.0
            happiness[voter.id] = h
        return happiness

    def borda_happiness(self, winner):
        """
        For Borda voting, we use a normalized linear score.
        If there are m candidates and the winner is at rank r (1-indexed),
          H_i = (m - r) / (m - 1)
        so that a top-ranked candidate gives H_i = 1 and the last-ranked gives H_i = 0.
        """
        happiness = {}
        m = len(self.preference_matrix[0].preferences)
        for voter in self.preference_matrix:
            r = voter.preferences.index(winner) + 1
            h = (m - r) / (m - 1) if m > 1 else 1.0
            happiness[voter.id] = h
        return happiness

    def overall_happiness(self, happiness_dict):
        """Return the sum of all voters' happiness levels."""
        return sum(happiness_dict.values())
