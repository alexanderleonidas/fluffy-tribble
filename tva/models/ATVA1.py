from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from itertools import combinations
from collections import defaultdict
from tva.models.BTVA import BTVA
from tva.situation import Situation
from tva.enums import HappinessFunc, VotingScheme, StrategyType
import tqdm

class ATVA1(BTVA):
    def __init__(self):
        BTVA.__init__(self)

    
    def merge_strategies(self, bury, bullets, comp):
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
  
        if len(voter_indexes)<2:
            return [False]
        return [True, merged, voter_indexes]


    def group_voters_by_preferences(self, preferences, strategies, stratVoters, winner):
        voter_groups = defaultdict(list)
        # Do not consider collusion with voters who have their original preference as winner

        dissatisfied_voters = {p.voter_id: p.preferences for  p in preferences if p.preferences[0] != winner and p.voter_id in strategies}
        # Now group by common aim in first two preferences of all voters. 
        # Also if voter has unique preference (losing candidates), group them by themselves, and check their eligibility in joining another group with popular aim
        # it is eligible if the position of the other voter aim is lower than the current winner. 
        for voter, pref in dissatisfied_voters.items():
            added = False
            for aim in voter_groups.keys():
                if (len(set(pref[:2]) & set(aim)) > 0):
                    voter_groups[aim].append(voter)
                    added = True
            if not added:
                voter_groups[pref[0]].append(voter)
                if pref[1]!=winner:
                    voter_groups[pref[1]].append(voter) 

                
        
        
        # find single voter groups 
        single_voter_groups = {key: voters for key, voters in voter_groups.items() if len(voters) == 1}
        # Get all aims
        aims = {key for key, voters in voter_groups.items() if len(voters) > 1}

        # These single groups can represent compromoising since they are voters with no common top preference.
        # Try find a new aim for these single groups (expecting compromise to another aim).
        # Check for each aim among other voter groups if the aim (the candidate) position is before the winner position in the og preference of the single voter.
        #If it is, then we can append this voter to the "aim" (compromising to popular strategic aim)
        for key, voters in single_voter_groups.items():
            delete_key = False  # Initialize here for each group
            voter = voters[0]
            pref = preferences[voter].preferences
            for aim in aims:
                if pref.index(aim) < pref.index(winner):  
                    voter_groups[aim].append(voter)            
            del voter_groups[key]
                
        return voter_groups
      

    # Get combos of voter collusions based on group (can be up to size 3 (adjustable))
    def form_voter_pairs(self, voter_groups, max_size):
        coalitions = []
        for key, voters in voter_groups.items():
            if len(voters) < 2:
                continue  
            for size in range(2, min(max_size + 1, len(voters) + 1)):
                for coalition in combinations(voters, size):
                    coalitions.append((key, coalition))
        return coalitions


    def collude(self, coalitions, rank, original_total_happiness, strategies, situation:Situation, voting_scheme:VotingScheme, happiness_func:HappinessFunc):
       
        #Sort the coalitions by the number of voters. e.g. ('A', (1,3,5)) has 3 voters with aim to have A win. Sorts it by most voters with aim.
        coalitions = sorted(coalitions, key=lambda x: -len(x[1]))

        #best_coalition = None
        #max_happiness_gain = float('-inf')
        #coalition_results = []
        processed_coalitions=set()

        for aim, voters in coalitions:
            temp_situation: Situation = deepcopy(situation)
            best_strategies = self.select_best_strategy(voters, strategies, rank, aim)
    
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
                temp_election = self.schemes.apply_voting_scheme(voting_scheme, temp_situation.voters, return_ranking=True)
                new_winner = temp_election[0]
                temp_total_h, temp_individual_h, new_winner = temp_situation.calculate_happiness(situation.voters, happiness_func, voting_scheme, return_winner=True) # type: ignore
                
                # Get happiness gain sum among all colluding voters. We choose the biggest one.
                happiness_gain = sum(temp_individual_h.get(voter, 0) - strategies[voter][0]['original_individual_happiness'] for voter in voters)
                total_happiness_gain=temp_total_h - original_total_happiness
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
                        'original_winner': rank[0][0],
                        'simulated_winner': new_winner,
                        'colluder_total_happiness_gain': happiness_gain,
                        'new_total_happiness': temp_total_h,
                        'total_happiness_gain': total_happiness_gain,
                        'colluders_original_happiness': colluders_original_happiness,
                        'colluders_strategic_happiness': colluders_strategy_happiness,
                        'colluders_happiness_gain': individual_happiness_gain,
                        'strategic_collusion_action' : strategic_actions
                    }
                
                    return coalition_info

        return False


    def select_best_strategy(self, voters, strategies, rank, aim):
        selected_strategies = {}
        winner=rank[0][0]
        
        # Check for each voter in group based on aim
        for voter in voters:
            if voter not in strategies:
                continue
            for strategy in strategies[voter]:
                #AIM which is one of their top 2 prefs should be the first in their strategy. the og winner should be in bottom half.
                if strategy['strategy'][0] == aim and winner in strategy['strategy'][len(strategy['strategy']) // 2:]:
                    selected_strategies[voter] = strategy
                    break

        return selected_strategies

    def analyse_multiple_ATVA(self, situations,num_repititions, voting_scheme, happiness_func, max_collusion, verbose=False):
  
        counter = 0
        happinessGain = 0

        for situation in situations:

            bullet=self.analyse_single(situation,happiness_func,voting_scheme,StrategyType.BULLET,False)
            bury=self.analyse_single(situation,happiness_func,voting_scheme,StrategyType.BURYING,False)
            comp=self.analyse_single(situation,happiness_func,voting_scheme,StrategyType.COMPROMISING,False)
            
            result = self.merge_strategies(bury=bury,bullets=bullet,comp=comp)
            if result[0]:  # if there is more than one voter with strategic moves. Otherwise no collusion possible
                merged_strats, stratVoters = result[1], result[2]  
                total_h, individual_h, original_winner = situation.calculate_happiness(situation.voters, happiness_func, voting_scheme, return_winner=True) # type: ignore
                original_rank = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, True, True)

                groups = self.group_voters_by_preferences(situation.voters, merged_strats, stratVoters, original_winner)
                coalitions = self.form_voter_pairs(groups, max_collusion)

                collusion_stats=self.collude(coalitions, original_rank, total_h, merged_strats, situation, voting_scheme, happiness_func)
            
                if collusion_stats and isinstance(collusion_stats, dict):
                    counter+=1
                    if collusion_stats['new_total_happiness'] > total_h:
                        happinessGain += 1
                        
                        
        atva1_risk = (counter / (num_repititions)) * 100
        happiness_improvement= (happinessGain/num_repititions)*100

        return {
            'atva1_risk': atva1_risk,
            'happiness_improvement': happiness_improvement
        }

    def analyse_multiple_for_comparison(self, situations, voting_scheme, happiness_func, verbose=False):
        btva_risks = {StrategyType.BULLET:0.0, 
                      StrategyType.BURYING:0.0,
                      StrategyType.COMPROMISING: 0.0}
        
        for k, _ in btva_risks.items():
            risk = self.analyse_multiple(situations, voting_scheme, happiness_func, k, verbose)
            btva_risks[k] = risk
        
        return btva_risks
           

           
