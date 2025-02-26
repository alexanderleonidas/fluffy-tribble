from collections import Counter, defaultdict
from tva.voter import Voter
from tva.enums import VotingScheme

class Schemes:
    def print_results(self, situation, verbose=False):
        winner1, counts1 = self.__voting_for_n(-1, situation.voters, True)
        winner2, counts2 = self.__voting_for_n(2, situation.voters, True)
        winner3, counts3 = self.__borda_voting(situation.voters, True)
        if verbose:
            print("Anti plurality:", winner1, counts1, "\nTwo voting:", winner2, counts2, "\nBorda:", winner3, counts3)
        else:
            print("Anti plurality:", winner1, ", Two voting:", winner2, ", Borda:", winner3)
    
    def apply_voting_scheme(self, voting_scheme:VotingScheme, voters:list[Voter], return_scores=False, return_ranking=False):
        """ Apply the specified voting scheme to determine the winner. """
        if voting_scheme == VotingScheme.PLURALITY:
            return self.__voting_for_n(1, voters, return_scores, return_ranking)
        elif voting_scheme == VotingScheme.VOTE_FOR_TWO:
            return self.__voting_for_n(2, voters, return_scores, return_ranking)
        elif voting_scheme == VotingScheme.ANTI_PLURALITY:
            return self.__voting_for_n(-1, voters, return_scores, return_ranking)
        # elif voting_scheme == VotingScheme.BORDA:
        return self.__borda_voting(voters, return_scores, return_ranking)

    def __voting_for_n(self, n, voters:list[Voter], return_scores=False, return_ranking=False):
        # Get all unique candidates
        all_candidates = self.__get_all_candidates(voters)
        # Get top n choices
        top_n_choices = [voter.preferences[:n] for voter in voters]
        # Flatten list
        all_votes = [candidate for pair in top_n_choices for candidate in pair]
        # Count occurrences of each candidate
        vote_counts = Counter(all_votes)
        ranked_candidates = self.__get_rankings(all_candidates, vote_counts)
        if return_scores:
            return ranked_candidates[0], dict(vote_counts)
        elif return_ranking:
            return ranked_candidates
        elif return_scores and return_ranking:
            return ranked_candidates, dict(vote_counts)
        return ranked_candidates[0]

    def __borda_voting(self, voters:list[Voter], return_scores=False, return_ranking=False):
        """ Apply Borda count voting to determine the winner. """
        # Get all unique candidates
        all_candidates = self.__get_all_candidates(voters)
        # Dictionary to store candidate scores
        scores = defaultdict(int)
        # Get the maximum number of candidates in any voter's list
        m = max(len(voter.preferences) for voter in voters)
        for voter in voters:
            # Number of points to assign to each candidate
            for rank, candidate in enumerate(voter.preferences):
                # Assign points
                scores[candidate] += (m - 1 - rank)
        ranked_candidates = self.__get_rankings(all_candidates, scores)
        if return_scores:
            return ranked_candidates[0], dict(scores)
        elif return_ranking:
            return ranked_candidates
        elif return_scores and return_ranking:
            return ranked_candidates, dict(scores)
        return ranked_candidates[0]

    @staticmethod
    def __get_all_candidates(voters):
        """Extract all unique candidates from all voter preferences."""
        all_candidates = set()
        for voter in voters:
            all_candidates.update(voter.preferences)
        return all_candidates

    @staticmethod
    def __get_rankings(all_candidates, vote_counts):
        # Ensure all candidates are in the vote_counts dictionary
        for candidate in all_candidates:
            if candidate not in vote_counts:
                vote_counts[candidate] = 0
        # Sort candidates by vote count (descending) and then alphabetically for ties
        rankings = sorted(vote_counts.items(), key=lambda item: (-item[1], item[0]))
        # Extract just the candidates in ranked order
        ranked_candidates = [candidate for candidate, _ in rankings]
        return ranked_candidates
    
