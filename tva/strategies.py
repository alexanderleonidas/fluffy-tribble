from schemes import Schemes
from situation import Situation
from voter import Voter
from enums import VotingScheme
import copy

class Strategies:
    def __init__(self):
        self.schemes = Schemes()
        
    def is_any_strategy_good(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme) -> bool:
        """Returns a new set of preferences for the voter to improve its happiness"""
        
        bullet_preferences = self.__bullet_vote(situation, voter_index, voting_scheme)
        if bullet_preferences:
            return bullet_preferences
        return self.__bury_compromise(situation, voter_index, voting_scheme)
    
    def __bullet_vote(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme) -> bool:
        """voting for just one alternative, despite having the option to vote for several"""
        voter: Voter = situation.voters[voter_index]
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, voting_scheme)
        voters: list[Voter] =  copy.deepcopy(situation.voters)
        
        bullet_preferences:list[list[str]] = self.__get_bullet_preferences(voter.preferences)
        for pref in bullet_preferences:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = pref
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, voting_scheme)
            if happiness > original_happiness:
                return True
        return False
    
    def __get_bullet_preferences(self, elements:list[str]):
        """
        Given an array of elements return a list of lists where each list contains only the first element plus one of the other alternatives
        """
        first_element = elements[0]
        return [[first_element, e] for e in elements[1:]]

    def __bury_compromise(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme) -> bool:
        """Returns true if the voter can benefit from a strategic vote"""
        voter: Voter = situation.voters[voter_index]
        
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, voting_scheme)
        voters: list[Voter] =  copy.deepcopy(situation.voters)

        # Get all preference permutations
        permutations:list[list[str]] = self.__get_permutations(voter.preferences)
        for perm in permutations:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = perm
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, voting_scheme)
            if happiness > original_happiness:
                return True
        return False
        
    def __get_permutations(self, elements):
        """
        Given an array of elements print every possible way to permutate the alternatives
        Skip the first element
        """
        first_element = elements[0]
        elements = elements[1:]
        return self.__permute(elements, first_element)

    def __permute(self, elements, first_element):
        if len(elements) == 1:
            return [elements]
        else:
            perms = []
            for i, e in enumerate(elements):
                for perm in self.__permute(elements[:i] + elements[i+1:], first_element):
                    perms.append([first_element, e] + perm)
            return perms
        

situation = Situation(num_voters=4, num_candidates=4, seed=42)
strategies = Strategies()
schemes = Schemes()

print(situation)
winner1, scores = schemes.borda_voting(situation.voters, return_scores=True)
print("Borda:", winner1, scores)

# for i in range(4):
i = 2
bullet_vote_improvement = strategies.is_any_strategy_good(situation, i, VotingScheme.BORDA)
bury_compromise_improvement = strategies.is_any_strategy_good(situation, i, VotingScheme.BORDA)
print(f"Voter {i} can improve happiness with bullet vote: {bullet_vote_improvement}, with bury compromise: {bury_compromise_improvement}")

