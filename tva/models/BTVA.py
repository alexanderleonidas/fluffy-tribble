from tva.situation import Situation
from tva.happiness import Happiness
from tva.schemes import Schemes
from tva.strategies import Strategies
from tva.enums import HappinessFunc, VotingScheme, StrategyType
from tqdm import tqdm


class BTVA:
    def __init__(self):
        self.happiness = Happiness()
        self.schemes = Schemes()
        self.strategy = Strategies()

    @staticmethod
    def display_strategic_data(data):
        for voter_id, strategies in data.items():
            print(f"Voter {voter_id} Strategies:")
            for strategy in strategies:
                print(f"  Strategy: {strategy['strategy']}")
                print(f"    - Strategic Winner: {strategy['strategic_winner']}")
                print(f"    - Strategic Individual Happiness: {strategy['strategic_individual_happiness']:.3f}")
                print(f"    - Original Individual Happiness: {strategy['original_individual_happiness']:.3f}")
                print(f"    - Strategic Total Happiness: {strategy['strategic_total_happiness']:.3f}")
                print(f"    - Original Total Happiness: {strategy['original_total_happiness']:.3f}")
                print("  ")

    def analyse_single(self, situation:Situation, happiness_func: HappinessFunc, voting_scheme: VotingScheme, strategy_type: StrategyType, verbose=False) -> dict[int, list[dict[str, float|int]]]:
        output_dict = {}
        total_h, individual_h, original_winner = situation.calculate_happiness(happiness_func, voting_scheme, return_winner=True) # type: ignore
        
        if verbose:
            print(f'{situation.get_num_candidates()} Candidates, {situation.get_num_voters()} Voters')
            print('Voting Scheme: ', voting_scheme)
            print('Strategy Type: ', strategy_type)
            print('Happiness Function: ', happiness_func)
            situation.print_preference_matrix()
            print(f'Original winner: {original_winner}')
            print(f'Total happiness: {total_h:.3f}')
            print('Individual happiness')
            print(" | ".join(f'Voter {k}: {h}' for k, h in individual_h.items()))

        # ANALYSE STRATEGIC SITUATIONS HERE AND RETURN THE DATA IN THE OUTPUT_DICT
        strategic_situations = self.strategy.get_strategic_preferences_for_all_voters(situation, voting_scheme, happiness_func, strategy_type, exhaustive_search=False)
        print(strategic_situations)
        if len(strategic_situations) != 0:
            for voter_id, strategic_situation in strategic_situations.items():
                s_i = []
                for strat in strategic_situation:
                    temp_total_h, temp_individual_h, temp_winner = strat.calculate_happiness(happiness_func, voting_scheme, return_winner=True) # type: ignore

                    # Choose only the strategies that increase a voters individual happiness
                    if temp_individual_h[voter_id] > individual_h[voter_id]:
                        s_ij = {
                                'strategy': strat.voters[voter_id].preferences,
                                'strategic_winner': temp_winner,
                                'strategic_individual_happiness': temp_individual_h[voter_id],
                                'original_individual_happiness': individual_h[voter_id],
                                'strategic_total_happiness': temp_total_h,
                                'original_total_happiness': total_h}
                        if s_ij: s_i.append(s_ij)

                output_dict[voter_id] = s_i
            if verbose: self.display_strategic_data(output_dict)
        else:
            return {}

        return output_dict

    def analyse_multiple(self, situations:list[Situation], voting_scheme, happiness_func, strategy_type, return_avg_happiness=False, verbose=False):
        print(len(situations), 'Repetitions')
        print(f'{situations[0].get_num_candidates()} Candidates, {situations[0].get_num_voters()} Voters')
        print('Voting Scheme: ', voting_scheme)
        print('Strategy Type: ', strategy_type)
        print('Happiness Function: ', happiness_func)
        print('Analysing experiment...')

        strategy_counter = 0
        strategic_happiness = 0
        honest_happiness = 0

        for situation in tqdm(situations):
            # Check if at least one voter has a good strategy
            strategic_winner = None
            strategic_h = None
            strategic_indiv_h = None
            honest_h, honest_indiv_h, honest_winner = situation.calculate_happiness(happiness_func, voting_scheme, return_winner=True)
            honest_happiness += honest_h
            for voter_index in range(situation.get_num_voters()):
                strategic_situations = self.strategy.get_strategic_preferences_for_voter(situation, voter_index, voting_scheme, happiness_func, strategy_type, False, verbose)
                if strategic_situations:
                    situation.voters[voter_index].preferences = strategic_situations.pop()
                    # Calculate happiness level for each voter
                    strategic_h, strategic_indiv_h, strategic_winner = situation.calculate_happiness(happiness_func, voting_scheme, return_winner=True)  # type: ignore
                    strategic_happiness += strategic_h
                    strategy_counter += 1
                    break

            if verbose:
                print(f"Honest winner: {honest_winner}")
                if strategic_winner: print(f"Strategic Winner: {strategic_winner}")
                print(f"Honest overall happiness: {honest_h:.3f}")
                if strategic_h: print(f"Strategic overall happiness: {strategic_h:.3f}")
                print('Honest individual happiness:')
                print(" | ".join(f'Voter {k}: {h}' for k, h in honest_indiv_h.items()))
                if strategic_indiv_h:
                    print('Strategic individual happiness:')
                    print(" | ".join(f'Voter {k}: {h}' for k, h in strategic_indiv_h.items()))

        if return_avg_happiness:
            if strategy_counter != 0: avg_strategic_happiness = strategic_happiness / strategy_counter
            else: avg_strategic_happiness = 0
            avg_honest_happiness = honest_happiness / len(situations)
            return (strategy_counter / len(situations)) * 100, avg_strategic_happiness, avg_honest_happiness
        return (strategy_counter / len(situations)) * 100

# Example Usage
# btva = BTVA()
# situation = Situation(10,5, seed=42)
# print('Original Situation: ')
# situation.print_preference_matrix()
# happiness_func = HappinessFunc.WEIGHTED_POSITIONAL
# voting_scheme = VotingScheme.VOTE_FOR_TWO
# strategy_type = StrategyType.BURYING
# sol = btva.analyse_single(situation, happiness_func, voting_scheme, strategy_type, True)