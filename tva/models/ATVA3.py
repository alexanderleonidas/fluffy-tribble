from copy import deepcopy
from tva.situation import Situation
from tva.enums import HappinessFunc, VotingScheme, StrategyType
from BTVA import BTVA
import random

class ATVA3(BTVA):
    def __init__(self):
        BTVA.__init__(self)

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