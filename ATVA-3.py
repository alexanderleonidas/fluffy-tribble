from copy import deepcopy
from tva.situation import Situation
from tva.happiness import Happiness
from tva.schemes import Schemes
from tva.voter import Voter
from tva.strategies import Strategies
from tva.enums import HappinessFunc, VotingScheme, StrategyType
import random

class ATVA3:
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
        original_election_outcome = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_ranking=True)
        if happiness_func == HappinessFunc.WEIGHTED_POSITIONAL or happiness_func == HappinessFunc.KENDALL_TAU:
            total_h, individual_h = self.happiness.calculate_ranked(situation.voters, original_election_outcome, happiness_func=happiness_func)
        else:
            total_h, individual_h = self.happiness.calculate(situation.voters, original_election_outcome[0], happiness_func)

        print(f'Original winner: {original_election_outcome[0]}')
        print(f'Total happiness: {total_h:.3f}')
        print('Individual happiness')
        print(" | ".join(f'Voter {k}: {h}' for k, h in individual_h.items()))


        # ANALYSE STRATEGIC SITUATIONS HERE AND RETURN THE DATA IN THE OUTPUT_DICT
        strategic_situations = self.strategy.analyse_situation(situation, voting_scheme, happiness_func, strategy_type, exhaustive_search=True)
        
        # You have to check, which of these strategic situations lower the overall happiness, since I couldn't do it in the strategies.py file

        # strategic_situation is a list of strategic preferences, so a list of lists
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

                    if temp_individual_h[voter_id] > individual_h[voter_id]:
                        s_ij = {'strategy': strat.voters[voter_id].preferences,
                                'strategic_winner': temp_winner,
                                'strategic_individual_happiness': temp_individual_h[voter_id],
                                'original_individual_happiness': individual_h[voter_id],
                                'strategic_total_happiness': temp_total_h,
                                'original_total_happiness': total_h}
                        s_i.append(s_ij)

                output_dict[voter_id] = s_i
        else:
            print('No good strategies found')

        return output_dict

    def monte_carlo_best_preferences(self, situation: Situation, voting_scheme: VotingScheme, num_simulations=1000, happiness_func=HappinessFunc.EXP):
        best_situation = None
        max_overall_happiness = -float('inf')
            
        for _ in range(num_simulations):
            sim_situation = deepcopy(situation)

            for voter in sim_situation.voters:
                if "?" in voter.preferences:
                    known_prefs = [c for c in voter.preferences if c != "?"]
                    missing_candidates = [c for c in sim_situation.candidates if c not in known_prefs]
                    random.shuffle(missing_candidates)
                    
                    simulated = []
                    missing_iter = iter(missing_candidates)
                    for entry in voter.preferences:
                        if entry == "?":
                            simulated.append(next(missing_iter))
                        else:
                            simulated.append(entry)
                    simulated.extend(list(missing_iter))
                    voter.preferences = simulated
                
            if happiness_func in (HappinessFunc.WEIGHTED_POSITIONAL, HappinessFunc.KENDALL_TAU):
                election_ranking = self.schemes.apply_voting_scheme(voting_scheme, sim_situation.voters, return_ranking=True)
                overall_happiness, _ = self.happiness.calculate_ranked(sim_situation.voters, election_ranking, happiness_func)
            else:
                winner = self.schemes.apply_voting_scheme(voting_scheme, sim_situation.voters)
                overall_happiness, _ = self.happiness.calculate(sim_situation.voters, winner, happiness_func)
                
            if overall_happiness > max_overall_happiness:
                max_overall_happiness = overall_happiness
                best_situation = sim_situation
            
        return best_situation, max_overall_happiness


atva = ATVA3()
situation = Situation(10,5, seed=42, info=0.5)
print('Original Situation: ')
situation.print_preference_matrix()
situation, _ = atva.monte_carlo_best_preferences(situation, VotingScheme.BORDA)
print('\nAfter Monte Carlo Simulation preferences:\n')
situation.print_preference_matrix()
happiness_func = HappinessFunc.EXP
voting_scheme = VotingScheme.VOTE_FOR_TWO
strategy_type = StrategyType.BURYING
# ranking = Schemes().apply_voting_scheme(voting_scheme, situation.voters)
sol = atva.analyse(situation, happiness_func, voting_scheme, strategy_type) # type: ignore
atva.display_strategic_data(sol)