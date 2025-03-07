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

    def analyse_single(self, num_voters: int, num_candidates: int, happiness_func: HappinessFunc, voting_scheme: VotingScheme, strategy_type: StrategyType, verbose=False):
        output_dict = {}
        situation = Situation(num_voters, num_candidates, seed=42)
        total_h, individual_h, original_winner = situation.calculate_happiness(situation.voters, happiness_func, voting_scheme, return_winner=True) # type: ignore
        
        if verbose:
            print(f'{num_candidates} Candidates, {num_voters} Voters')
            print('Voting Scheme: ', voting_scheme)
            print('Strategy Type: ', strategy_type)
            print('Happiness Function: ', happiness_func)
            situation.print_preference_matrix()
            print(f'Original winner: {original_winner}')
            print(f'Total happiness: {total_h:.3f}')
            print('Individual happiness')
            print(" | ".join(f'Voter {k}: {h}' for k, h in individual_h.items()))

        # ANALYSE STRATEGIC SITUATIONS HERE AND RETURN THE DATA IN THE OUTPUT_DICT
        strategic_situations = self.strategy.analyse_situation(situation, voting_scheme, happiness_func, strategy_type, exhaustive_search=True)
        # print(strategic_situations)
        if len(strategic_situations) != 0:
            for voter_id, strategic_situation in strategic_situations.items():
                s_i = []
                for strat in strategic_situation:

                    if happiness_func == HappinessFunc.WEIGHTED_POSITIONAL or happiness_func == HappinessFunc.KENDALL_TAU:
                        temp_election_ranking = self.schemes.apply_voting_scheme(voting_scheme, strat.voters, return_ranking=True)
                        temp_winner = temp_election_ranking[0]
                        temp_total_h, temp_individual_h = self.happiness.calculate_ranked(situation.voters, temp_election_ranking, happiness_func)
                    else:
                        temp_winner = self.schemes.apply_voting_scheme(voting_scheme, strat.voters)
                        temp_total_h, temp_individual_h = self.happiness.calculate(situation.voters, temp_winner[0], happiness_func)

                    # Choose only the strategies that increase a voters individual happiness
                    if temp_individual_h[voter_id] > individual_h[voter_id]:
                        s_ij = {
                                'strategy': strat.voters[voter_id].preferences,
                                'strategic_winner': temp_winner,
                                'strategic_individual_happiness': temp_individual_h[voter_id],
                                'original_individual_happiness': individual_h[voter_id],
                                'strategic_total_happiness': temp_total_h,
                                'original_total_happiness': total_h}
                        s_i.append(s_ij)

                output_dict[voter_id] = s_i
            if verbose: self.display_strategic_data(output_dict)
        else:
            print('No good strategies found')

        return output_dict

    def analyse_multiple(self, num_repetitions, num_voters, num_candidates, voting_scheme, happiness_func, strategy_type, verbose=False):
        print(num_repetitions, 'Repetitions')
        print(f'{num_candidates} Candidates, {num_voters} Voters')
        print('Voting Scheme: ', voting_scheme)
        print('Strategy Type: ', strategy_type)
        print('Happiness Function: ', happiness_func)
        print('Analysing experiment...')
        strategy_counter = 0
        for _ in tqdm(range(num_repetitions)):
            situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
            # Check if at least one voter has a good strategy
            for voter_index in range(num_voters):
                if self.strategy.get_strategic_preferences_for_voter(situation, voter_index, voting_scheme, happiness_func, strategy_type, True, verbose):
                    strategy_counter += 1
                    break

            # Happiness level for each voter
            if verbose:
                total_h, _, honest_winner = situation.calculate_happiness(situation.voters, happiness_func, voting_scheme, return_winner=True) # type: ignore
                print(f"Honest winner: {honest_winner}")
                print(f"Honest overall happiness: {total_h:.3f}")

        return (strategy_counter/num_repetitions) * 100

# Example Usage
# btva = BTVA()
# situation = Situation(10,5, seed=42)
# print('Original Situation: ')
# situation.print_preference_matrix()
# happiness_func = HappinessFunc.WEIGHTED_POSITIONAL
# voting_scheme = VotingScheme.VOTE_FOR_TWO
# strategy_type = StrategyType.BURYING
# sol = btva.analyse_single(situation, happiness_func, voting_scheme, strategy_type, True)