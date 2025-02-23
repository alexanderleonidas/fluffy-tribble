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
        return self.__bury(situation, voter_index, voting_scheme, happiness_func, verbose=False)
    
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
        first_element = elements[0]
        return [[first_element, e] for e in elements[1:]]
    
    def __swap(self, situation:Situation, voter_id:int, candidate1_index:int, candidate2_index:int, verbose=False):
        if verbose:
            print(f"Swapping {situation.voters[voter_id].preferences[candidate1_index]} and {situation.voters[voter_id].preferences[candidate2_index]}")
        situation.voters[voter_id].preferences[candidate1_index], situation.voters[voter_id].preferences[candidate2_index] = situation.voters[voter_id].preferences[candidate2_index], situation.voters[voter_id].preferences[candidate1_index]

    def __bury(self, situation:Situation, voter_index:int, voting_scheme:VotingScheme, happiness_func:Happiness, verbose=False):
        original_voter = situation.voters[voter_index]
        original_preferences = situation.voters[voter_index].preferences
        # If the original winner is the first preference of the voter, return False
        original_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_scores=True)
        original_winner_index = original_preferences.index(original_winner) # type: ignore
        original_winner_happiness = original_voter.calculate_happiness(original_winner, happiness_func)

        if verbose:
            print(original_preferences)
            print("Borda:", original_winner, scores)

        if original_winner_index == 0:
            return False
        return self.__recursive_bury(situation, voter_index, [original_preferences], original_voter, original_winner_happiness, voting_scheme, happiness_func, verbose)

    def __recursive_bury(self, situation:Situation, voter_index:int, past_preferences:list, original_voter:Voter, original_winner_happiness:float, voting_scheme:VotingScheme, happiness_func:Happiness, verbose=False):
        starting_preferences = situation.voters[voter_index].preferences
        num_candidates = len(starting_preferences)
        modified_situation = copy.deepcopy(situation)

        # Save the original winner
        starting_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_scores=True)
        starting_winner_index = starting_preferences.index(starting_winner) # type: ignore
        # Initialize the current winner
        
        # Keep moving the winner to the right until it chantes the winner or reaches the end of the loop
        for i in range(starting_winner_index+1, num_candidates):
            self.__swap(modified_situation, voter_index, i-1, i, verbose)
            new_preferences = modified_situation.voters[voter_index].preferences
            if verbose:
                print(new_preferences)

            if new_preferences in past_preferences:
                if verbose:
                    print("Loop detected")
                continue
            past_preferences.append(copy.deepcopy(new_preferences))

            current_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, modified_situation.voters, return_scores=True)
            current_winner_happiness = original_voter.calculate_happiness(current_winner, happiness_func)

        
            if verbose:
                print("Borda:", current_winner, scores)
            if current_winner != starting_winner:
                if current_winner_happiness > original_winner_happiness:
                    if verbose:
                        print("Found a winning strategy!")
                    return True
                else:
                    if verbose:
                        print("Winner changed")
                    found_winning_strategy = self.__recursive_bury(modified_situation, voter_index, past_preferences, original_voter, original_winner_happiness, voting_scheme, happiness_func, verbose)
                    if found_winning_strategy:
                        return True

        # If finished the loop, then the winner is still the same, so return False
        if verbose:
            print("Left recursion")
        return False
