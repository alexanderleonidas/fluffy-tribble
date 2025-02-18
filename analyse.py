from tva.situation import Situation
from tva.enums import VotingScheme, Happiness
from tva.strategies import Strategies

########## Choose experiment parameters ##########
# Number of experiments to run
nr_repetitions = 1000
# Number of Voters
num_voters = 4
# Number of Candidates
num_candidates = 4
# Voting Scheme
voting_scheme = VotingScheme.BORDA
strategies = Strategies()
# Happiness function
happiness_func = Happiness.EXP

strategy_counter = 0
for i in range(nr_repetitions):
    situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
    # Check if at least one voter has a good strategy
    for voter_index in range(num_voters):
        if strategies.is_any_strategy_good(situation, voter_index, voting_scheme, happiness_func):
            strategy_counter += 1
            break
        
print(strategy_counter/nr_repetitions)