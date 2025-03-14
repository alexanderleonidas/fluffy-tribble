from tva.enums import VotingScheme, StrategyType, HappinessFunc
from tva.models.BTVA import BTVA
from tva.situation import Situation

########## Choose experiment parameters ##########
# Number of experiments to run
num_repetitions = 100
# Number of Voters
num_voters = 6
# Number of Candidates
num_candidates = 5
# Voting Scheme
voting_scheme = VotingScheme.BORDA
# Strategy type
strategy_type = StrategyType.COMPROMISING
# Happiness function
happiness_func = HappinessFunc.KENDALL_TAU
# Verbose
verbose = False
##################################################


btva = BTVA()
situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
risk, avg_strat_happiness, avg_honest_happiness  = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, True, verbose)
print(f'Risk of strategic voting: {risk}%, Average Strategic Happiness: {avg_strat_happiness:.3f}, Average Honest Happiness: {avg_honest_happiness:.3f}')

# situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
# output = btva.analyse_single(situation, happiness_func, voting_scheme, strategy_type, True)
# print(len(output))