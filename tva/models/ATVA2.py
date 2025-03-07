from copy import deepcopy
from tva.situation import Situation
from tva.enums import HappinessFunc, VotingScheme, StrategyType
from tva.models.BTVA import BTVA
import numpy as np

class ATVA2(BTVA):
    def __init__(self):
        BTVA.__init__(self)

    def analyse_single(self, situation: Situation, happiness_func: HappinessFunc, voting_scheme: VotingScheme, strategy_type: StrategyType, verbose=False) -> dict[int, list[dict[str, float|int]]]:
        analysis = {}
        for voter in situation.voters[:1]:
            voter_index = voter.voter_id
            original_total_happiness, original_individual_happiness= situation.calculate_happiness(situation.voters, happiness_func, voting_scheme) # type: ignore

            strategic_preferences = self.strategy.apply_all_strategies_to_voter(situation,voter_index, voting_scheme, happiness_func, exhaustive_search=True, verbose=verbose)
        
            # Save my average happiness for each preference list
            preferences_happiness = []
            for _, preference_list in strategic_preferences.items():
                # For each set of preferences in the list, create a new situation
                for preferences in preference_list:
                    situation_copy = deepcopy(situation)
                    situation_copy.voters[voter_index].preferences = preferences
                    winner = self.schemes.apply_voting_scheme(voting_scheme, situation_copy.voters)
                    # Check the strategic options of each of my opponents, select the ones that maximize their happiness 
                    # then, calculate my happiness after they have chosen their best strategy
                    all_other_voter_ids = [voter.voter_id for voter in situation_copy.voters if voter.voter_id != voter_index]
                    my_happiness_list = []
                    total_happiness_list = []
                    for enemy_index in all_other_voter_ids:
                        enemy_situation = self.__find_situation_chosen_by_enemy(situation_copy, enemy_index, voting_scheme, happiness_func, verbose)
                        # Calculate my happiness after the enemy has chosen their best strategy
                        strategic_total_happiness, strategic_individual_happiness= enemy_situation.calculate_happiness(situation.voters, happiness_func, voting_scheme) # type: ignore

                        my_happiness = strategic_individual_happiness[voter_index]
                        my_happiness_list.append(my_happiness)
                        total_happiness_list.append(strategic_total_happiness)
                    # Calculate my average happiness over all options that my enemies would choose
                    my_average_happiness = np.mean(my_happiness_list)
                    average_total_happiness = np.mean(total_happiness_list)
                    preferences_happiness.append({
                        "strategy": preferences,
                        "strategic_winner":winner,
                        "strategic_individual_happiness": my_average_happiness,
                        'original_individual_happiness': original_individual_happiness[voter_index],
                        'strategic_total_happiness': average_total_happiness,
                        'original_total_happiness': original_total_happiness})

            analysis[voter_index] = preferences_happiness

        return analysis

    def __find_situation_chosen_by_enemy(self, situation:Situation, enemy_index:int, voting_scheme:VotingScheme, happiness_func:HappinessFunc, verbose:bool=False) -> Situation:
        enemy_strategies = self.strategy.apply_all_strategies_to_voter(situation,enemy_index, voting_scheme, happiness_func, exhaustive_search=True, verbose=verbose)
        
        # Save only the best strategy for each enemy
        best_enemy_situation = situation
        best_enemy_happiness = -1
        # Try all the strategies of the enemy voter
        for _, enemy_preference_list in enemy_strategies.items():
            for enemy_preferences in enemy_preference_list:
                enemy_situation = deepcopy(situation)
                enemy_situation.voters[enemy_index].preferences = enemy_preferences
                # Calculate the happiness of the enemy voter
                enemy_happiness = float(enemy_situation.calculate_individual_happiness(enemy_preferences, happiness_func, voting_scheme)) # type: ignore
                if enemy_happiness > best_enemy_happiness:
                    best_enemy_happiness = enemy_happiness
                    best_enemy_situation = enemy_situation
        return best_enemy_situation
    