import math
from tva.enums import HappinessFunc
from tva.voter import Voter

class Happiness:

    def calculate_ranked(self, preference_matrix:list[Voter], election_ranking:list, happiness_func:HappinessFunc):
        """Calculate total happiness and individual happiness for all voters based on ranked outcomes."""
        total_happiness = 0.0
        individual_happiness = {}
        for voter in preference_matrix:
            score = self.calculate_individual_ranked(voter.preferences, election_ranking, happiness_func)
            individual_happiness[voter.voter_id] = score
            total_happiness += score
        return total_happiness, individual_happiness

    def calculate_individual_ranked(self, preferences: list[str], election_ranking: list, happiness_func: HappinessFunc):
        """Calculate individual happiness based on the specified happiness function and ranked outcome."""
        if happiness_func == HappinessFunc.KENDALL_TAU:
            return self.__kendall_tau_happiness(preferences, election_ranking)
        elif happiness_func == HappinessFunc.WEIGHTED_POSITIONAL:
            return self.__weighted_positional_happiness(preferences, election_ranking)
        else:
            raise Exception(f'{happiness_func} cannot be used for this happiness calculation')

    def calculate(self, preference_matrix:list[Voter], winner:str, happiness_func:HappinessFunc):
        total_happiness = 0.0
        individual_happiness = {}
        for voter in preference_matrix:
            score = self.calculate_individual(voter.preferences, winner, happiness_func)
            individual_happiness[voter.voter_id] = score
            total_happiness += score # type: ignore
        return total_happiness, individual_happiness

    def calculate_individual(self, preferences: list[str], winner: str, happiness_func: HappinessFunc):
        """ Apply the specified voting scheme to determine the winner. """
        if happiness_func == HappinessFunc.LOG:
            return self.__logarithmic_happiness(preferences, winner)
        elif happiness_func == HappinessFunc.EXP:
            return self.__exponential_happiness(preferences, winner)
        elif happiness_func == HappinessFunc.LINEAR:
            return self.__linear_happiness(preferences, winner)
        else:
            raise Exception(f'{happiness_func} cannot be used for this happiness calculation')

    @staticmethod
    def __logarithmic_happiness(preferences: list[str], winner: str):
        """
        A logarithmic decay hapiness function.
        If the winning candidate is ranked r (1-indexed),
        H_i = 1 / log2(r + 1)
        so that a voter whose top candidate wins (r = 1) gets happiness 1.
        """
        r = preferences.index(winner) + 1  # convert to 1-index
        return 1 / math.log2(r + 1)

    @staticmethod
    def __exponential_happiness(preferences:list, winner: str, decay_alpha=0.1):
        """
        An exponential decay happiness function.
        Here we use a “shift” so that if the winner is a voter's top choice (r = 1),
        H_i = exp(-alpha*(1-1)) = exp(0) = 1.
        For lower-ranked outcomes, happiness decays as:
        H_i = exp(-alpha*(r-1))
        """
        r = preferences.index(winner) + 1
        return math.exp(-decay_alpha * (r - 1))

    @staticmethod
    def __linear_happiness(preferences:list, winner: str):
        """
        A normalized linear score happiness function.
        If there are m candidates and the winner is at rank r (1-indexed),
        H_i = (m - r) / (m - 1)
        so that a top-ranked candidate gives H_i = 1 and the last-ranked gives H_i = 0.
        """
        m = len(preferences)  # Number of candidates
        r = preferences.index(winner) + 1 if winner in preferences else 0
        return (m - r) / (m - 1) if m > 1 else 1.0

    @staticmethod
    def __kendall_tau_happiness(voter_prefs: list, election_ranking: list):
        """
        Calculates voter happiness using Kendall's Tau distance.

        Kendall's Tau measures the similarity between two rankings by counting
        concordant and discordant pairs. A normalized score is returned where
        1 represents perfect agreement and 0 represents complete disagreement.
        """
        # Type safety check - ensure we have lists
        if isinstance(voter_prefs, str):
            voter_prefs = [voter_prefs]
        if isinstance(election_ranking, str):
            election_ranking = [election_ranking]

        # Create a set of all candidates from both rankings
        all_candidates = set(voter_prefs).union(set(election_ranking))

        # Count concordant and discordant pairs
        concordant = 0
        discordant = 0
        total_pairs = 0

        for i, cand_i in enumerate(all_candidates):
            for j, cand_j in enumerate(all_candidates):
                if i >= j:  # Skip identical pairs and count each pair only once
                    continue

                # Skip if either candidate is not in both lists
                if cand_i not in voter_prefs or cand_j not in voter_prefs or \
                        cand_i not in election_ranking or cand_j not in election_ranking:
                    continue

                # Get ranks in both orderings
                rank_i_voter = voter_prefs.index(cand_i)
                rank_j_voter = voter_prefs.index(cand_j)

                rank_i_outcome = election_ranking.index(cand_i)
                rank_j_outcome = election_ranking.index(cand_j)

                # Check if pairs agree in ordering
                if (rank_i_voter < rank_j_voter and rank_i_outcome < rank_j_outcome) or \
                        (rank_i_voter > rank_j_voter and rank_i_outcome > rank_j_outcome):
                    concordant += 1
                else:
                    discordant += 1

                total_pairs += 1

        # Calculate normalized happiness (1 = perfect agreement, 0 = complete disagreement)
        if total_pairs == 0:
            return 1.0  # If no pairs to compare, assume perfect happiness

        return concordant / total_pairs

    @staticmethod
    def __weighted_positional_happiness(voter_prefs: list, election_ranking: list):
        """
        Calculates voter happiness using Weighted Positional Distance.

        This approach uses position-based weights to calculate how closely
        the election outcome matches a voter's preferences. Discrepancies
        in higher positions are weighted more heavily than lower positions.
        """
        # Type safety check - ensure we have lists
        if isinstance(voter_prefs, str):
            voter_prefs = [voter_prefs]
        if isinstance(election_ranking, str):
            election_ranking = [election_ranking]

        # Create a set of all candidates
        all_candidates = set(voter_prefs).union(set(election_ranking))
        n = len(all_candidates)

        if n <= 1:
            return 1.0  # Perfect happiness with only one candidate

        # Calculate position weights (linearly decreasing)
        weights = [n - i for i in range(n)]

        # Calculate weighted distance
        actual_distance = 0
        max_distance = 0

        for candidate in all_candidates:
            # Handle candidates that may not be in both lists
            if candidate in voter_prefs and candidate in election_ranking:
                pos_voter = voter_prefs.index(candidate)
                pos_outcome = election_ranking.index(candidate)

                # Apply weight based on position in voter's preferences
                weight = weights[pos_voter]
                actual_distance += weight * abs(pos_voter - pos_outcome)
                # Maximum possible distance for this candidate
                max_distance += weight * (n - 1)
            elif candidate in voter_prefs:
                # Candidate in voter prefs but not in outcome - worst case
                pos_voter = voter_prefs.index(candidate)
                weight = weights[pos_voter]
                actual_distance += weight * (n - 1)  # Maximum possible distance
                max_distance += weight * (n - 1)
            elif candidate in election_ranking:
                # Candidate in outcome but not in voter prefs
                # We can't assign a sensible weight, so we'll use average weight
                avg_weight = sum(weights) / n
                actual_distance += avg_weight * (n - 1)
                max_distance += avg_weight * (n - 1)

        # Normalize to [0,1], where 1 = perfect agreement
        if max_distance == 0:
            return 1.0  # Avoid division by zero

        happiness = 1 - (actual_distance / max_distance)
        return happiness