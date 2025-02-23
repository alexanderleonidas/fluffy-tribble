from tva.situation import Situation
from tva.enums import VotingScheme, Happiness
from tva.strategies import Strategies
from tva.schemes import Schemes

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
schemes = Schemes()
# Happiness function
happiness_func = Happiness.LOG

voters1 = [
    ['A', 'B', 'C', 'D'],
    ['B', 'C', 'D', 'A'],
    ['C', 'D', 'A', 'B'],
    ['D', 'A', 'B', 'C']
]
strategy_counter = 0
for i in range(nr_repetitions):
    situation = Situation(num_voters=num_voters, num_candidates=num_candidates, candidates=['A', 'B', 'C', 'D'], voters=voters1)
    # Check if at least one voter has a good strategy
    for voter_index in range(num_voters):
        if strategies.is_any_strategy_good(situation, voter_index, voting_scheme, happiness_func):
            strategy_counter += 1
            break

honest_winner = schemes.apply_voting_scheme(voting_scheme, situation.voters)
# Happiness level for each voter
for voter in situation.voters:
    print("Voter", voter.voter_id + 1, "happiness:", voter.calculate_happiness(honest_winner, happiness_func))
honest_overall_happiness = situation.average_happiness(honest_winner, happiness_func)
print("Honest winner:", honest_winner)
print("Honest overall happiness:", honest_overall_happiness)
risk = (strategy_counter/nr_repetitions) * 100

for voter in situation.voters:
    og_happiness_voter = voter.calculate_happiness(honest_winner, happiness_func)
    bullet_opt = strategies.bullet_options(situation, voter.voter_id, voting_scheme, happiness_func)
    bury_opt = strategies.bury_options(situation, voter.voter_id, voting_scheme, happiness_func)

    if bullet_opt or bury_opt:
        print(("-" * 50))  
        print(f"Strategic voting options for Voter {voter.voter_id + 1}:")
        print("v_ij | Ô | H̃_i | H_i | H̃ | H | ΔH")
    for mod_prefs, outcome, ind_hap in bury_opt:
        diff = ind_hap - og_happiness_voter
        overall = situation.average_happiness(outcome, happiness_func)
        print(f"BURYING: ({', '.join(mod_prefs)}) | {outcome} | {ind_hap:.2f} | {og_happiness_voter:.2f} | {overall:.2f} | {honest_overall_happiness:.2f} | +{diff:.2f}")
    for mod_prefs, outcome, ind_hap in bullet_opt:
        diff = ind_hap - og_happiness_voter
        overall = situation.average_happiness(outcome, happiness_func)
        print(f"BULLET: ({', '.join(mod_prefs)}) | {outcome} | {ind_hap:.2f} | {og_happiness_voter:.2f} | {overall:.2f} | {honest_overall_happiness:.2f} | +{diff:.2f}")

print("\nRisk of strategic voting:", risk, "%")
