from tva.schemes import Schemes
from tva.situation import Situation
from tva.voter import Voter
from tva.enums import VotingScheme, Happiness
import copy

class Strategies:
    def __init__(self):
        self.schemes = Schemes()
        
    def is_any_strategy_good(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> bool:
        """Returns a new set of preferences for the voter to improve its happiness"""
        
        bullet_preferences = self.__bullet_vote(situation, voter_index, voting_scheme, happiness_func)
        if bullet_preferences:
            return bullet_preferences
        return self.__bury_compromise(situation, voter_index, voting_scheme, happiness_func)
    
    def __bullet_vote(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> bool:
        """voting for just one alternative, despite having the option to vote for several"""
        voter: Voter = situation.voters[voter_index]
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, happiness_func)
        voters: list[Voter] =  copy.deepcopy(situation.voters)
        
        bullet_preferences:list[list[str]] = self.__get_bullet_preferences(voter.preferences)
        for pref in bullet_preferences:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = pref
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, happiness_func)
            if happiness > original_happiness:
                return True
        return False
    
    def __get_bullet_preferences(self, elements:list[str]):
        """
        Given an array of elements return a list of lists with each element as a list
        """
        return [[elements[0]]]

    def __bury_compromise(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> bool:
        """Returns true if the voter can benefit from a strategic vote"""
        voter: Voter = situation.voters[voter_index]
        
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, happiness_func)
        voters: list[Voter] =  copy.deepcopy(situation.voters)

        # Get all preference permutations
        permutations:list[list[str]] = self.__get_permutations(voter.preferences)
        for perm in permutations:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = perm
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, happiness_func)
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
        
    def bullet_options(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> list:
        """voting for just one alternative, despite having the option to vote for several"""
        voter: Voter = situation.voters[voter_index]
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, happiness_func)
        voters: list[Voter] =  copy.deepcopy(situation.voters)
        strategic_options = []
        
        bullet_preferences:list[list[str]] = self.__get_bullet_preferences(voter.preferences)
        for pref in bullet_preferences:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = pref
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, happiness_func)
            if happiness > original_happiness:
                strategic_options.append((pref, new_winner, happiness))
        return strategic_options
    
    def bury_options(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> list:
        voter: Voter = situation.voters[voter_index]
        
        # Save the original happiness of this voter
        original_winner:str = self.schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        original_happiness = voter.calculate_happiness(original_winner, happiness_func)
        voters: list[Voter] =  copy.deepcopy(situation.voters)
        strategic_options = []

        # Get all preference permutations
        permutations:list[list[str]] = self.__get_permutations(voter.preferences)
        for perm in permutations:
            # Find the winner of the voting scheme with the new preference
            voters[voter_index].preferences = perm
            # print("Permutation:", original_preferences)
            new_winner:str = self.schemes.apply_voting_scheme(voting_scheme, voters) # type: ignore
            # Calculate the happiness of the voter with the new preference
            happiness = voter.calculate_happiness(new_winner, happiness_func)
            if happiness > original_happiness:
                strategic_options.append((perm, new_winner, happiness))
        return strategic_options
    