from collections import Counter, defaultdict
from tva.voter import Voter
from tva.enums import VotingScheme



class Schemes:
    def print_results(self, situation, verbose=True):
        winner1, counts1 = self.anti_plurality_voting(situation.voters, True)
        winner2, counts2 = self.voting_for_two(situation.voters, True)
        winner3, counts3 = self.borda_voting(situation.voters, True)
        if verbose:
            print("Anti plurality:", winner1, counts1, "\nTwo voting:", winner2, counts2, "\nBorda:", winner3, counts3)
        else:
            print("Anti plurality:", winner1, ", Two voting:", winner2, ", Borda:", winner3)
    
    def apply_voting_scheme(self, voting_scheme:VotingScheme, voters:list[Voter]):
        """ Apply the specified voting scheme to determine the winner. """
        if voting_scheme == VotingScheme.PLURALITY:
            return self.plurality_voting(voters)
        elif voting_scheme == VotingScheme.VOTE_FOR_TWO:
            return self.voting_for_two(voters)
        elif voting_scheme == VotingScheme.ANTI_PLURALITY:
            return self.anti_plurality_voting(voters)
        elif voting_scheme == VotingScheme.BORDA:
            return self.borda_voting(voters)
    
    def plurality_voting(self, voters:list[Voter], return_scores=False):
        """ Apply plurality voting to determine the winner. """
        # Get first-choice votes
        first_choices = [voter.preferences[0] for voter in voters]
        # Count occurrences of each candidate
        vote_counts = Counter(first_choices)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get) # type: ignore
        if return_scores:
            return winner, dict(vote_counts)
        return winner

    def __voting_for_n(self, n, voters:list[Voter], return_scores=False):
        # Get top n choices
        top_n_choices = [voter.preferences[:n] for voter in voters]
        # Flatten list
        all_votes = [candidate for pair in top_n_choices for candidate in pair]
        # Count occurrences of each candidate
        vote_counts = Counter(all_votes)
        # Candidate with most votes
        winner = max(vote_counts, key=vote_counts.get) # type: ignore
        if return_scores:
            return winner, dict(vote_counts)
        return winner

    def voting_for_two(self, voters:list[Voter], return_scores=False):
        """ Apply vote-for-two voting to determine the winner. """
        return self.__voting_for_n(2, voters, return_scores)

    def anti_plurality_voting(self, voters:list[Voter], return_scores=False):
        """ Apply anti-plurality voting to determine the winner. """
        # Exclude last choice
        return self.__voting_for_n(-1, voters, return_scores)

    def borda_voting(self, voters:list[Voter], return_scores=False):
        scores = defaultdict(int)
        # Get the maximum number of candidates in any voter's list
        total_candidates = max(len(voter.preferences) for voter in voters)
        for voter in voters:
        # Wenn ein Voter bullet votet, enthält seine Liste nur einen Kandidaten.
            m = total_candidates if len(voter.preferences) == 1 else len(voter.preferences)
            for rank, candidate in enumerate(voter.preferences):
                scores[candidate] += (m - 1 - rank)
        winner = max(scores, key=scores.get)
        if return_scores:
            return winner, dict(scores)
        return winner

    

    def overall_happiness(self, happiness_dict):
        """Return the sum of all voters' happiness levels."""
        return sum(happiness_dict.values())