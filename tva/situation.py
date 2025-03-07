import random
import string
from tabulate import tabulate
from tva.voter import Voter
from tva.schemes import Schemes
from tva.happiness import Happiness
from tva.enums import HappinessFunc, VotingScheme

schemes = Schemes()
happiness = Happiness()

class Situation:
    def __init__(self, num_voters:int, num_candidates:int, seed=None, candidates=None, voters=None, info=None):
        assert num_candidates > 0, "Number of candidates must be greater than 0."
        assert num_candidates <= 20, "If the number of candidates is greater than 9, there are too many permutations to calculate quickly."
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
        # Extract voter IDs as header row
        headers = [" "] + [f"V{voter.voter_id}" for voter in self.voters]

        # Convert Voter objects to lists of preferences
        matrix = [voter.preferences for voter in self.voters]

        # Transpose the matrix so that ranks are rows and voters are columns
        transposed = list(zip(*matrix))

        # Add rank numbers
        table_data = [[f"Rank {i + 1}"] + list(row) for i, row in enumerate(transposed)]

        # Print formatted table without grid lines
        print("Preference Matrix:")
        print(tabulate(table_data, headers=headers, tablefmt="plain"))

    def get_num_candidates(self):
        return len(self.candidates)
    
    def get_num_voters(self):
        return len(self.voters)
    
    def calculate_individual_happiness(self, individual_preferences, happiness_func:HappinessFunc, voting_scheme:VotingScheme, return_winner=False):
        if happiness_func == HappinessFunc.WEIGHTED_POSITIONAL or happiness_func == HappinessFunc.KENDALL_TAU:
            election_ranking = schemes.apply_voting_scheme(voting_scheme, self.voters, return_ranking=True)
            winner = election_ranking[0]
            winner_happiness = happiness.calculate_individual_ranked(individual_preferences, election_ranking, happiness_func)
        else:
            winner = schemes.apply_voting_scheme(voting_scheme, self.voters)
            winner_happiness = happiness.calculate_individual(individual_preferences, winner, happiness_func)
        if return_winner:
            return winner_happiness, winner
        else:
            return winner_happiness
        
    def calculate_happiness(self, preference_matrix:list[Voter], happiness_func:HappinessFunc, voting_scheme:VotingScheme, return_winner=False):
        if happiness_func == HappinessFunc.WEIGHTED_POSITIONAL or happiness_func == HappinessFunc.KENDALL_TAU:
            election_ranking = schemes.apply_voting_scheme(voting_scheme, self.voters, return_ranking=True)
            winner = election_ranking[0]
            total_happiness, individual_happiness = happiness.calculate_ranked(preference_matrix, election_ranking, happiness_func)
        else:
            winner = schemes.apply_voting_scheme(voting_scheme, self.voters)
            total_happiness, individual_happiness = happiness.calculate(preference_matrix, winner, happiness_func)
        if return_winner:
            return total_happiness, individual_happiness, winner
        else:
            return total_happiness, individual_happiness
    