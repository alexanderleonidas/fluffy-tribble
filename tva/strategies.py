from tva.schemes import Schemes
from tva.situation import Situation
from tva.voter import Voter
from tva.enums import VotingScheme, Happiness
import copy

class Strategies:
    def __init__(self):
        self.schemes = Schemes()
        
    def is_any_strategy_good(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> dict[str,list[str]|None]:
        """Returns a new set of preferences for the voter to improve its happiness"""
        
        winning_strategies: dict[str,list[str]|None] = {}
        bullet_preferences = self.__bullet_vote(situation, voter_index, voting_scheme, happiness_func)
        winning_strategies["bullet"] = bullet_preferences
        bury_preferences = self.__bury(situation, voter_index, voting_scheme, happiness_func, verbose=False)
        winning_strategies["bury"] = bury_preferences
        return winning_strategies
    
    def __bullet_vote(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:Happiness) -> list[str]|None:
        """voting for just one alternative, despite having the option to vote for several"""
        voter: Voter = situation.voters[voter_index]
        # Save the original happiness of this voter
        current_winner:str = schemes.apply_voting_scheme(voting_scheme, situation.voters) # type: ignore
        # If the current winner is the same as the voter's first preference, there is no need to bullet vote
        if current_winner == voter.preferences[0]:
            return None

        original_happiness = voter.calculate_happiness(current_winner, happiness_func)
        new_situation = copy.deepcopy(situation)

        # If the winner is not the first preference of the voter, remove the winner from the voter's preferences
        # Repeat as long as the list of preferences is not empty
        while len(new_situation.voters[voter_index].preferences) > 0:
            if current_winner not in new_situation.voters[voter_index].preferences:
                return None
            
            new_situation.voters[voter_index].preferences.remove(current_winner)
            current_winner:str = schemes.apply_voting_scheme(voting_scheme, new_situation.voters) # type: ignore
            current_happiness = voter.calculate_happiness(current_winner, happiness_func)
            if current_happiness > original_happiness:
                return new_situation.voters[voter_index].preferences
            # If the happiness of the voter is not increased, try to remove the second preference
        return None
    
    def __swap(self, situation:Situation, voter_id:int, candidate1_index:int, candidate2_index:int, verbose=False):
        if verbose:
            print(f"Swapping {situation.voters[voter_id].preferences[candidate1_index]} and {situation.voters[voter_id].preferences[candidate2_index]}")
        situation.voters[voter_id].preferences[candidate1_index], situation.voters[voter_id].preferences[candidate2_index] = situation.voters[voter_id].preferences[candidate2_index], situation.voters[voter_id].preferences[candidate1_index]

    def __bury(self, situation:Situation, voter_index:int, voting_scheme:VotingScheme, happiness_func:Happiness, exhaustive_search=False, verbose=False) -> None | list[str]:
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
            return None
        past_preferences = [original_preferences]
        did_find_winning_strategy = self.__recursive_bury(situation, voter_index, past_preferences, original_voter, original_winner_happiness, voting_scheme, happiness_func, exhaustive_search, [], verbose)
        if did_find_winning_strategy:
            return past_preferences[-1]
        return None

    def __recursive_bury(self, situation:Situation, voter_index:int, past_preferences:list, original_voter:Voter, original_winner_happiness:float, voting_scheme:VotingScheme, happiness_func:Happiness, exhaustive_search=False, winning_strategies=[], verbose=False):
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
                    if exhaustive_search:
                        winning_strategies.append(new_preferences)
                    else:
                        return True
                else:
                    if verbose:
                        print("Winner changed")
                    found_winning_strategy = self.__recursive_bury(modified_situation, voter_index, past_preferences, original_voter, original_winner_happiness, voting_scheme, happiness_func, exhaustive_search, winning_strategies, verbose)
                    if found_winning_strategy:
                        if exhaustive_search:
                            winning_strategies.append(new_preferences)
                        else:
                            return True

        # If finished the loop, then the winner is still the same, so return False
        if verbose:
            print("Left recursion")
        return False

    def __get_indexes_to_iterate(self, preferences:list[str], scores:dict[str,int]):
        # Given a list of preferences and the scores of those preferences, return a list of indexes of candidates to the left of the current winner
        # The current winner is the candidate with the highest score
        # Return the indexes of preferences sorted by score in descending order
        # If the current winner is at index 0, return an empty list
        current_winner = max(scores, key=scores.get) # type: ignore
        current_winner_index = preferences.index(current_winner)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        print("Sorted scores:", sorted_scores)
        candidates = [x[0] for x in sorted_scores[1:]]
        print("Candidates:", candidates)

        indexes_to_try = []
        for i in candidates:
            candidate_index = preferences.index(i)
            if candidate_index < current_winner_index:
                indexes_to_try.append(candidate_index)
        return indexes_to_try

    def __compromise(self, situation:Situation, voter_index:int, voting_scheme:VotingScheme, happiness_func:Happiness, exhaustive_search=False, verbose=False) -> None | list[str]:
        # Copy the situation
        new_situation = copy.deepcopy(situation)
        original_voter = new_situation.voters[voter_index]
        original_preferences = new_situation.voters[voter_index].preferences
        # If the original winner is the first preference of the voter, return False
        original_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, new_situation.voters, return_scores=True)
        original_winner_index = original_preferences.index(original_winner) # type: ignore
        original_winner_happiness = original_voter.calculate_happiness(original_winner, happiness_func)

        if verbose:
            print(original_preferences)
            print("Borda:", original_winner, scores)

        if original_winner_index == 0:
            return None
        
        all_winning_preferences = []
        indexes_to_iterate = self.__get_indexes_to_iterate(original_preferences, scores) # type: ignore
        # Loop over all candidates to the left of the original winner sorted by score
        for i in indexes_to_iterate:
            # Move that candidate to the first position
            self.__swap(new_situation, voter_index, i, 0, verbose=verbose)
            # Check if the winner changed and if the voter is happier
            new_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, new_situation.voters, return_scores=True)
            new_winner_happiness = original_voter.calculate_happiness(new_winner, happiness_func)

            if verbose:
                print(new_situation.voters[voter_index].preferences)
                print("Borda:", new_winner, scores)

            if new_winner != original_winner and new_winner_happiness > original_winner_happiness:
                if exhaustive_search:
                    all_winning_preferences.append(new_situation.voters[voter_index].preferences)
                    print("Found a winning preference")
                else:
                    print("Found a winning preference")
                    return new_situation.voters[voter_index].preferences

        if all_winning_preferences == []:
            return None
        return all_winning_preferences