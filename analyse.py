from tva.situation import Situation
from tva.schemes import Schemes
from tva.enums import VotingScheme
from tva.strategies import Strategies

strategies = Strategies()
voting_scheme = VotingScheme.BORDA
nr_repetitions = 1000
num_voters = 4

strategy_counter = 0
for i in range(nr_repetitions):
    situation = Situation(num_voters=num_voters, num_candidates=4)
    # Check if at least one voter has a good strategy
    for voter_index in range(num_voters):
        if strategies.is_any_strategy_good(situation, voter_index, voting_scheme):
            strategy_counter += 1
            break
        
print(strategy_counter/nr_repetitions)