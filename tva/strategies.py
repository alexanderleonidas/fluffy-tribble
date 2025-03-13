from tva.schemes import Schemes
from tva.situation import Situation
from tva.happiness import Happiness
from tva.voter import Voter
from tva.enums import VotingScheme, HappinessFunc, StrategyType
from copy import deepcopy


class Strategies:
    def __init__(self):
        self.schemes = Schemes()
        self.happiness = Happiness()
        
    def apply_all_strategies_to_voter(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, exhaustive_search=False, verbose=False) -> dict[StrategyType, list[list[str]]]:
        """Apply all strategies to a single voter"""
        strategies = {}
        for strategy in StrategyType:
            if verbose:
                print(f"Applying strategy {strategy}")
            strategic_preferences = self.get_strategic_preferences_for_voter(situation, voter_index, voting_scheme, happiness_func, strategy, exhaustive_search=exhaustive_search, verbose=False)
            if verbose:
                print(strategic_preferences)
            if strategic_preferences is not None:
                strategies[strategy] = strategic_preferences
        return strategies

    def get_strategic_preferences_for_all_voters(self, situation: Situation, voting_scheme:VotingScheme, happiness_func:HappinessFunc, strategy:StrategyType, exhaustive_search=False, verbose=False) -> dict[int, list[Situation]]:
        """Returns a dictionary of voters and the strategic situations that increase their happiness after applying a single StrategyType"""
        strategic_situations = {}
        for voter in situation.voters:
            if verbose:
                print('voter ',voter.voter_id)
            strategic_preferences = self.get_strategic_preferences_for_voter(situation, voter.voter_id, voting_scheme, happiness_func, strategy, exhaustive_search=exhaustive_search)
            # print(strategic_preferences)
            if strategic_preferences is None:
                continue
            
            situations = []
            print(strategic_preferences)
            for preferences in strategic_preferences:
                copied_situation = deepcopy(situation)
                copied_situation.voters[voter.voter_id].preferences = preferences
                situations.append(copied_situation)

            strategic_situations[voter.voter_id] = situations
        return strategic_situations

    def get_strategic_preferences_for_voter(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, strategy:StrategyType, exhaustive_search, verbose=False) -> list[list[str]] | None:
        """Returns a new set of preferences for the voter to improve its happiness"""
        
        if strategy == StrategyType.BULLET:
            return self.bullet_vote(situation, voter_index, voting_scheme, happiness_func, exhaustive_search=exhaustive_search)
        elif strategy == StrategyType.BURYING:
            return self.bury(situation, voter_index, voting_scheme, happiness_func, exhaustive_search=exhaustive_search, verbose=verbose)
        # elif strategy == StrategyType.COMPROMISING:
        return self.compromise(situation, voter_index, voting_scheme, happiness_func, exhaustive_search=exhaustive_search, verbose=verbose)
    
    def bullet_vote(self, situation: Situation, voter_index: int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, exhaustive_search=False) -> None | list[list[str]]:
        """voting for just one alternative, despite having the option to vote for several"""
        voter: Voter = situation.voters[voter_index]
        original_happiness, current_winner = situation.calculate_individual_happiness(voter.preferences, happiness_func, voting_scheme, return_winner=True) # type: ignore
        if current_winner == voter.preferences[0]:
            return None

        new_situation = deepcopy(situation)

        winning_strategies = []
        # If the winner is not the first preference of the voter, remove the winner from the voter's preferences
        # Repeat as long as the list of preferences is not empty
        while len(new_situation.voters[voter_index].preferences) > 0:
            if current_winner not in new_situation.voters[voter_index].preferences:
                return None
            
            new_situation.voters[voter_index].preferences.remove(current_winner)
            current_happiness, current_winner = new_situation.calculate_individual_happiness(voter.preferences, happiness_func, voting_scheme, return_winner=True) # type: ignore

            if current_happiness > original_happiness:
                new_preferences = new_situation.voters[voter_index].preferences
                if exhaustive_search:
                    winning_strategies.append(new_preferences)
                else:
                    return [new_preferences]
            # If the happiness of the voter is not increased, try to remove the second preference
        
        if not winning_strategies:
            return None
        return winning_strategies
    
    def __swap(self, situation:Situation, voter_id:int, candidate1_index:int, candidate2_index:int, verbose=False):
        if verbose:
            print(f"Swapping {situation.voters[voter_id].preferences[candidate1_index]} and {situation.voters[voter_id].preferences[candidate2_index]}")
        situation.voters[voter_id].preferences[candidate1_index], situation.voters[voter_id].preferences[candidate2_index] = situation.voters[voter_id].preferences[candidate2_index], situation.voters[voter_id].preferences[candidate1_index]

    def bury(self, situation:Situation, voter_index:int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, exhaustive_search=False, verbose=False) -> None | list[list[str]]:
        original_voter = situation.voters[voter_index]
        original_preferences = situation.voters[voter_index].preferences

        if happiness_func == HappinessFunc.WEIGHTED_POSITIONAL or happiness_func == HappinessFunc.KENDALL_TAU:
            election_ranking, scores = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_ranking=True, return_scores=True)
            original_winner = election_ranking[0]
            original_winner_index = original_preferences.index(original_winner)
            original_winner_happiness = self.happiness.calculate_individual_ranked(original_preferences, election_ranking, happiness_func)
        else:
            original_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_scores=True)
            original_winner_index = original_preferences.index(original_winner) # type: ignore
            original_winner_happiness = self.happiness.calculate_individual(original_voter.preferences, original_winner, happiness_func)

        if verbose:
            print(original_preferences)
            print("Borda:", original_winner, scores)

        # If the original winner is the first preference of the voter, return False
        if original_winner_index == 0:
            return None
        past_preferences = [original_preferences]
        winning_strategies = []
        _ = self.__recursive_bury(situation, voter_index, past_preferences, original_voter, original_winner_happiness, voting_scheme, happiness_func, exhaustive_search, winning_strategies, verbose)
        if not winning_strategies:
            return None
        return winning_strategies

    def __recursive_bury(self, situation:Situation, voter_index:int, past_preferences:list, original_voter:Voter, original_winner_happiness:float, voting_scheme:VotingScheme, happiness_func:HappinessFunc, exhaustive_search=False, winning_strategies:list=[], verbose=False):
        starting_preferences = situation.voters[voter_index].preferences
        num_candidates = len(starting_preferences)
        modified_situation = deepcopy(situation)
        # Save the original winner
        starting_winner, scores = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_scores=True)
        starting_winner_index = starting_preferences.index(starting_winner) # type: ignore
        # Initialize the current winner
        
        # Keep moving the winner to the right until it changes the winner or reaches the end of the loop
        for i in range(starting_winner_index+1, num_candidates):
            self.__swap(modified_situation, voter_index, i-1, i, verbose)
            new_preferences = modified_situation.voters[voter_index].preferences
            if verbose:
                print(new_preferences)

            if new_preferences in past_preferences:
                if verbose:
                    print("Loop detected")
                continue
            past_preferences.append(deepcopy(new_preferences))
            current_winner_happiness, current_winner = modified_situation.calculate_individual_happiness(original_voter.preferences, happiness_func, voting_scheme, return_winner=True) # type: ignore

            if current_winner != starting_winner:
                if verbose:
                    print("Winner changed")

                # If the voter is happier, then we found a winning strategy 
                if current_winner_happiness > original_winner_happiness:
                    if verbose:
                        print("Found a winning strategy!")
                    if exhaustive_search:
                        winning_strategies.append(new_preferences)
                    else:
                        return True
                    
                found_winning_strategy = self.__recursive_bury(modified_situation, voter_index, past_preferences, original_voter, original_winner_happiness, voting_scheme, happiness_func, exhaustive_search, winning_strategies, verbose)
                if found_winning_strategy and not exhaustive_search:
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
        candidates = [x[0] for x in sorted_scores[1:]]

        indexes_to_try = []
        for i in candidates:
            candidate_index = preferences.index(i)
            if candidate_index < current_winner_index:
                indexes_to_try.append(candidate_index)
        return indexes_to_try

    def compromise(self, situation:Situation, voter_index:int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, exhaustive_search=False, verbose=False) -> None | list[list[str]]:
        # Copy the situation
        new_situation = deepcopy(situation)
        original_voter = new_situation.voters[voter_index]
        original_preferences = new_situation.voters[voter_index].preferences
        # If the original winner is the first preference of the voter, return False
        original_winner_happiness, original_winner = new_situation.calculate_individual_happiness(original_voter.preferences, happiness_func, voting_scheme, return_winner=True) # type: ignore
        
        original_winner_index = original_voter.preferences.index(original_winner) # type: ignore
        _, scores = self.schemes.apply_voting_scheme(voting_scheme, new_situation.voters, return_scores=True)
        
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
            new_winner_happiness, new_winner = new_situation.calculate_individual_happiness(original_voter.preferences, happiness_func, voting_scheme, return_winner=True) # type: ignore
        
            if verbose:
                print(new_situation.voters[voter_index].preferences)

            if new_winner != original_winner and new_winner_happiness > original_winner_happiness:
                if exhaustive_search:
                    all_winning_preferences.append(new_situation.voters[voter_index].preferences)
                    if verbose: print("Found a winning preference")
                else:
                    if verbose: print("Found a winning preference")
                    return [new_situation.voters[voter_index].preferences]

        if exhaustive_search:
            if not all_winning_preferences:
                return None
            else:
                return all_winning_preferences
        else:
            return None
