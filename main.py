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

btva = BTVA()
# risk = btva.analyse_multiple(num_repetitions, num_voters, num_candidates, voting_scheme, happiness_func, strategy_type, verbose)
# print(f'Risk of strategic voting: {risk}%')
situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
btva.analyse_single(situation, happiness_func, voting_scheme, strategy_type, True)


# for voter in situation.voters:
#     og_happiness_voter = voter.calculate_happiness(honest_winner, happiness_func)
#     bullet_opt = strategies.bullet_options(situation, voter.voter_id, voting_scheme, happiness_func)
#     bury_opt = strategies.bury_options(situation, voter.voter_id, voting_scheme, happiness_func)

#     if bullet_opt or bury_opt:
#         print(("-" * 50))  
#         print(f"Strategic voting options for Voter {voter.voter_id + 1}:")
#         print("v_ij | Ô | H̃_i | H_i | H̃ | H | ΔH")
#     for mod_prefs, outcome, ind_hap in bury_opt:
#         diff = ind_hap - og_happiness_voter
#         overall = situation.total_happiness(outcome, happiness_func)
#         print(f"BURYING: ({', '.join(mod_prefs)}) | {outcome} | {ind_hap:.2f} | {og_happiness_voter:.2f} | {overall:.2f} | {honest_overall_happiness:.2f} | +{diff:.2f}")
#     for mod_prefs, outcome, ind_hap in bullet_opt:
#         diff = ind_hap - og_happiness_voter
#         overall = situation.total_happiness(outcome, happiness_func)
#         print(f"BULLET: ({', '.join(mod_prefs)}) | {outcome} | {ind_hap:.2f} | {og_happiness_voter:.2f} | {overall:.2f} | {honest_overall_happiness:.2f} | +{diff:.2f}")

# print(f"\nRisk of strategic voting: {risk:.2f}%")
