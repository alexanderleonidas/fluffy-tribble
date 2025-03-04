from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from itertools import combinations
from collections import defaultdict
from tva.models.BTVA import BTVA
from tva.situation import Situation
from tva.enums import HappinessFunc, VotingScheme, StrategyType

class ATVA1(BTVA):
    def __init__(self):
        BTVA.__init__(self)

    
    def merge_strategies(self, bury, bullets, comp):
        # Merge bury, bullets and comp strategies

        merged = defaultdict(list)
        for strategy_dict in [bury, bullets, comp]:
            for voter_id, strategies in strategy_dict.items():
                if strategies:  # Ensure the voter has strategies and not empty []
                    existing_strategies = {tuple(s['strategy']) for s in merged[voter_id]}
                    for strategy in strategies:
                        strategy_tuple = tuple(strategy['strategy'])
                        if strategy_tuple not in existing_strategies:
                            merged[voter_id].append(strategy)
                            existing_strategies.add(strategy_tuple)
        merged={k: v for k, v in merged.items() if v}
        voter_indexes = list(merged.keys())
        #print(f"MERGED: {merged}")

        print(f"VOTERS THAT HAVE STRATS: {voter_indexes}")
        if len(voter_indexes)<2:
            print("No collusions found due to limited strategic moves in the situation")
            return False
        return True, merged, voter_indexes 
    

      

    def group_voters_by_preferences(self, preferences, strategies, stratVoters, election_ranking):
        voter_groups = defaultdict(list)
        winner = election_ranking[0][0]
        # Do not consider collusion with voters who have their original preference as winner

        dissatisfied_voters = {i: p for i, p in enumerate(preferences.voters) if p.preferences[0] != winner and i in strategies}
        # Now group by common aim in first two preferences of all voters. 
        # Also if voter has unique preference (losing candidates), group them by themselves, and check their eligibility in joining another group with popular aim
        # it is eligible if the position of the other voter aim is lower than the current winner. 
        for voter, pref in dissatisfied_voters.items():
            added = False
            for aim in voter_groups.keys():
                if (len(set(pref.preferences[:2]) & set(aim)) > 0):
                    voter_groups[aim].append(voter)
                    added = True
                    break
            if not added:
                voter_groups[pref.preferences[0]].append(voter)
                
        print("")
        print(f"Voter groups based on common top pref and unique prefs : {voter_groups}")
        print("")
        
        
        # find single voter groups 
        single_voter_groups = {key: voters for key, voters in voter_groups.items() if len(voters) == 1}
        # Get all aims
        aims = {key for key, voters in voter_groups.items() if len(voters) > 1}
        print(f"aims combined: {aims}")
        print("")
        # These single groups can represent compromoising since they are voters with no common top preference.
        # Try find a new aim for these single groups (expecting compromise to another aim).
        # Check for each aim among other voter groups if the aim (the candidate) position is before the winner position in the og preference of the single voter.
        #If it is, then we can append this voter to the "aim" (compromising to popular strategic aim)
        for key, voters in single_voter_groups.items():
            voter = voters[0]
            pref = preferences.voters[voter].preferences
            for aim in aims:
                if pref.index(aim) < pref.index(winner):  
                    voter_groups[aim].append(voter)
                    del voter_groups[key]
                    
        return voter_groups
      
    # Get combos of voter collusions based on group (can be up to size 3 (adjustable))
    def form_voter_pairs(self, voter_groups, max_size=3):
        coalitions = []
        for key, voters in voter_groups.items():
            if len(voters) < 2:
                continue  
            for size in range(2, min(max_size + 1, len(voters) + 1)):
                for coalition in combinations(voters, size):
                    coalitions.append((key, coalition))
        return coalitions


    def collude(self, coalitions, original_election_outcome, strategies, situation, voting_scheme, happiness_func):
        winner = original_election_outcome[0][0]
        #Sort the coalitions by the number of voters. e.g. ('A', (1,3,5)) has 3 voters with aim to have A win. Sorts it by most voters with aim.
        coalitions = sorted(coalitions, key=lambda x: -len(x[1]))
        print(f"Sorted coalitions: {coalitions}")

        #best_coalition = None
        #max_happiness_gain = float('-inf')
        #coalition_results = []
        processed_coalitions=set()

        for aim, voters in coalitions:
            temp_situation = deepcopy(situation)
            best_strategies = self.select_best_strategy(voters, strategies, winner, aim)
    
            # Filter out voters who don't have a strategy towards aim
            voters = tuple(voter for voter in voters if voter in best_strategies)

            if not voters or voters in processed_coalitions:
                continue  # Skip if empty or already checked coalitions

            processed_coalitions.add(voters)
            
            # IF we removed voters based on finding strategies, we must ensure there is more than one agent who can collude
            if len(voters)>1:
            # Change the preferences to the colluding preferences.
                for voter in voters:
                    temp_situation.voters[voter].preferences = best_strategies[voter]['strategy']
                        

                # Get new result
                temp_election = self.schemes.apply_voting_scheme(voting_scheme, temp_situation.voters, True, True)
                new_winner = temp_election[0][0]

                # Calculate happiness
                if happiness_func in [HappinessFunc.WEIGHTED_POSITIONAL, HappinessFunc.KENDALL_TAU]:
                    temp_total_h, temp_individual_h = self.happiness.calculate_ranked(situation.voters, temp_election[0], happiness_func)
                else:
                    temp_total_h, temp_individual_h = self.happiness.calculate(situation.voters, temp_election[0][0], happiness_func)

                # Get happiness gain sum among all colluding voters. We choose the biggest one.
                happiness_gain = sum(temp_individual_h.get(voter, 0) - strategies[voter][0]['original_individual_happiness'] for voter in voters)
                
                happiness_valid = any(
                    temp_individual_h.get(voter, 0) > strategies[voter][0]['original_individual_happiness'] for voter in voters) and all(temp_individual_h.get(voter, 0) >= strategies[voter][0]['original_individual_happiness'] for voter in voters)
                
                # Compute happiness gain for each voter and store as a dictionary
                individual_happiness_gain = {
                    voter: temp_individual_h.get(voter, 0) - strategies[voter][0]['original_individual_happiness']
                    for voter in voters
                }
                #list dictionary of colluding voters happiness after colluding
                colluders_strategy_happiness = {
                    voter: temp_individual_h.get(voter, 0) 
                    for voter in voters
                }
                #list dictionary of original happiness of the colluding voters
                colluders_original_happiness = {
                    voter: strategies[voter][0]['original_individual_happiness']
                    for voter in voters
                }
                strategic_actions = {
                    voter: temp_situation.voters[voter].preferences
                    for voter in voters
                }
                
                if happiness_valid:
                    coalition_info = {
                        'coalition': voters,
                        'original_winner': winner,
                        'simulated_winner': new_winner,
                        'total_happiness_gain': happiness_gain,
                        'new_total_happiness': temp_total_h,
                        'colluders_original_happiness': colluders_original_happiness,
                        'colluders_strategic_happiness': colluders_strategy_happiness,
                        'colluders_happiness_gain': individual_happiness_gain,
                        'strategic_collusion_action' : strategic_actions
                    }
                    print("")
                    print("COALITION FOUND:")
                    print(coalition_info)
                    return coalition_info
                #coalition_results.append(coalition_info)

                # Track best coalition
                #if happiness_gain > max_happiness_gain:
                    #max_happiness_gain = happiness_gain
                    #best_coalition = coalition_info
                
                #return coalition_info
          

        # Print the best coalition
        #if best_coalition:
            #print("")
            #print("Best Coalition:")
            #print(best_coalition)
        print("No collusions found")
        return False

    def select_best_strategy(self, voters, strategies, original_winner, aim):
        selected_strategies = {}
        # Check for each voter in group based on aim
        for voter in voters:
            if voter not in strategies:
                continue
            for strategy in strategies[voter]:
                #AIM which is one of their top 2 prefs should be the first in their strategy. the og winner should be in bottom half.
                if strategy['strategy'][0] == aim and original_winner in strategy['strategy'][len(strategy['strategy']) // 2:]:
                    selected_strategies[voter] = strategy
                    break
        #print("")
        #print(f"Selected strategies: {selected_strategies}")
        return selected_strategies

atva = ATVA1()
#situation = Situation(30, 8, seed=220)
situation = Situation(15, 8, seed=120)

preferences = situation
happiness_func = HappinessFunc.WEIGHTED_POSITIONAL
voting_scheme = VotingScheme.VOTE_FOR_TWO
strategy_types = [StrategyType.BULLET, StrategyType.BURYING, StrategyType.COMPROMISING]

bullets = atva.analyse_single(situation, happiness_func, voting_scheme, StrategyType.BULLET, True)
bury = atva.analyse_single(situation, happiness_func, voting_scheme, StrategyType.BURYING, False)
comp = atva.analyse_single(situation, happiness_func, voting_scheme, StrategyType.COMPROMISING, False)

#print(f"BULLET STRATS: {bullets}")
#print(f"BURY STRATS: {bury}")
#print(f"COMP STRATS: {comp}")

print("-------------------------------------")
print("ATVA1 collusion information:")

result = atva.merge_strategies(bullets, bury, comp)

if result:  # if there is more than one voter with strategic moves. Otherwise no collusion possible
    merged_strats, stratVoters = result[1], result[2]  
    
    original_election_outcome = atva.schemes.apply_voting_scheme(voting_scheme, preferences.voters, True, True)
    print("")
    print(f"original election outcome : {original_election_outcome}")

    groups = atva.group_voters_by_preferences(preferences, merged_strats, stratVoters, original_election_outcome)
    coalitions = atva.form_voter_pairs(groups, 5)

    atva.collude(coalitions, original_election_outcome, merged_strats, situation, voting_scheme, happiness_func)
