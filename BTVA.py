from copy import deepcopy
from tva.situation import Situation
from tva.happiness import Happiness
from tva.schemes import Schemes
from tva.voter import Voter
from tva.strategies import Strategies
from tva.enums import HappinessFunc, VotingScheme, StrategyType


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

    def analyse(self, situation: Situation, happiness_func: HappinessFunc, voting_scheme: VotingScheme, strategy_type: StrategyType):
        output_dict = {}
        original_winner = self.schemes.apply_voting_scheme(voting_scheme, situation.voters)
        total_h, individual_h = self.happiness.calculate(situation.voters, original_winner[0], happiness_func)
        print(f'Original winner: {original_winner[0]}')
        print(f'Total happiness: {total_h:.3f}')
        print(f'Individual happiness: {individual_h}')


        strategic_situations = self.strategy.analyse_situation(situation, voting_scheme, happiness_func, strategy_type)
        # TODO: 
        # You have to check, which of these strategic situations lower the overall happiness, since I couldn't do it in the strategies.py file

        # strategic_situation is a list of strategic preferences, so a list of lists
        for voter_id, strategic_situation in strategic_situations.items():
            s_i = []
            for strat in strategic_situation:
                temp_winner = self.schemes.apply_voting_scheme(voting_scheme, strat.voters)
                # original_preferences = situation.voters[voter_id].preferences
                temp_total_h, temp_individual_h = self.happiness.calculate(situation.voters, temp_winner[0], happiness_func)
                print('Strategic individual happiness: ', temp_individual_h[voter_id])
                print('Original individual happiness: ', individual_h[voter_id])
                if temp_individual_h[voter_id] > individual_h[voter_id]:
                    s_ij = {'strategy': strat.voters[voter_id].preferences,
                            'strategic_winner': temp_winner,
                            'strategic_individual_happiness': temp_individual_h[voter_id],
                            'original_individual_happiness': individual_h[voter_id],
                            'strategic_total_happiness': temp_total_h,
                            'original_total_happiness': total_h}
                    s_i.append(s_ij)

            output_dict[voter_id] = s_i

        return output_dict


btva = BTVA()
situation = Situation(4,4)
print('Original Situation: ')
situation.print_preference_matrix()
happiness_func = HappinessFunc.LOG
voting_scheme = VotingScheme.PLURALITY
strategy_type = StrategyType.COMPROMISING
# ranking = Schemes().apply_voting_scheme(voting_scheme, situation.voters)
sol = btva.analyse(situation, happiness_func, voting_scheme, strategy_type) # type: ignore
btva.display_strategic_data(sol)