from tva.enums import VotingScheme, StrategyType, HappinessFunc
from tva.models.BTVA import BTVA
from tva.situation import Situation

########## Choose experiment parameters ##########
# Number of experiments to run
num_repetitions = 10
# Number of Voters
num_voters = 20
# Number of Candidates
num_candidates = 6
# Voting Scheme
voting_scheme = VotingScheme.VOTE_FOR_TWO
# Strategy type
strategy_type = StrategyType.COMPROMISING
# Happiness function
happiness_func = HappinessFunc.KENDALL_TAU
# Verbose
verbose = False
##################################################


btva = BTVA()
# situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
# risk = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, verbose)
# print(f'Risk of strategic voting: {risk}%')
situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
btva.analyse_single(situation, happiness_func, voting_scheme, strategy_type, True)
