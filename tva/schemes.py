from collections import Counter, defaultdict


class Schemes:
    def __init__(self, preference_matrix):
        self.preference_matrix = preference_matrix

    def plurality_voting(self):
        """ Apply plurality voting to determine the winner. """
        # Get first-choice votes
        first_choices = [voter.preferences[0] for voter in self.preference_matrix]
        # Count occurrences of each candidate
        vote_counts = Counter(first_choices)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get)

        return winner


    def voting_for_two(self):
        """ Apply vote-for-two voting to determine the winner. """
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
        """ Apply anti-plurality voting to determine the winner. """
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
        """ Apply Borda count voting to determine the winner. """
        # Get total number of candidates
        num_candidates = len(self.preference_matrix[0].preferences)
        # Dictionary to store candidate scores
        scores = defaultdict(int)
        for voter in self.preference_matrix:
            for rank, candidate in enumerate(voter.preferences):
                # Assign points
                scores[candidate] += (num_candidates - 1 - rank)
        # Candidate with most points
        winner = max(scores, key=scores.get)
        return winner