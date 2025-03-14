from tva.models.BTVA import BTVA
from tva.situation import Situation
from tva.enums import VotingScheme, HappinessFunc, StrategyType
from copy import deepcopy
import itertools
from tqdm import tqdm
import pandas as pd
from tabulate import tabulate

class ATVA4(BTVA):
    """
    Advanced Tactical Voting Analyst that drops limitation #4:
    Considers situations where multiple voters vote strategically simultaneously,
    rather than analyzing one voter at a time.
    
    The ATVA4 risk is measured using Monte Carlo simulations as follows:
      For each simulation, we determine the maximum number of voters (the coalition size)
      that can improve their happiness by switching their vote strategically.
      Then the ATVA4 risk is given by:
      
          ATVA4 risk (%) = (sum(max_strategic_voters over all simulations) / (num_simulations * total_voters)) * 100
      
      Additionally, the percentage of simulations in which the strategic outcome yields a higher 
      total happiness than the honest outcome is computed as the "happiness improvement rate."
    """
    
    def __init__(self, max_strategic_voters=3):
        super().__init__()
        self.max_strategic_voters = max_strategic_voters

    def evaluate_strategic_combination(self, situation, voter_preferences, voting_scheme, 
                                       happiness_func, honest_winner, honest_individual_happiness):
        """
        Evaluate a specific combination of strategic voting preferences.
        Returns the outcome and happiness metrics if beneficial, None otherwise.
        """
        test_situation = deepcopy(situation)
        
        # Apply the strategic preferences to test situation
        for voter_id, prefs in voter_preferences:
            test_situation.voters[voter_id].preferences = prefs
            
        # Calculate new outcome and happiness
        if happiness_func in [HappinessFunc.KENDALL_TAU, HappinessFunc.WEIGHTED_POSITIONAL]:
            new_ranking = self.schemes.apply_voting_scheme(voting_scheme, test_situation.voters, return_ranking=True)
            new_winner = new_ranking[0]
            new_total_happiness, new_individual_happiness = self.happiness.calculate_ranked(
                situation.voters, new_ranking, happiness_func)
        else:
            new_winner = self.schemes.apply_voting_scheme(voting_scheme, test_situation.voters)
            new_total_happiness, new_individual_happiness = self.happiness.calculate(
                situation.voters, new_winner, happiness_func)
            
        # Check if any strategic voter benefits
        strategic_voters = [voter_id for voter_id, _ in voter_preferences]
        any_voter_benefits = False
        collective_action_required = True  # Track if this is truly a multi-voter only strategy
        individual_gains = {}
        
        for voter_id in strategic_voters:
            old_happiness = honest_individual_happiness[voter_id]
            new_happiness = new_individual_happiness[voter_id]
            happiness_gain = new_happiness - old_happiness
            individual_gains[voter_id] = happiness_gain
            
            if happiness_gain > 0:
                any_voter_benefits = True
                if len(strategic_voters) > 1:
                    solo_effective = self._is_effective_alone(
                        situation, voter_id, voter_preferences, 
                        voting_scheme, happiness_func, honest_individual_happiness
                    )
                    if solo_effective:
                        collective_action_required = False
            
        if any_voter_benefits:
            return {
                'voter_ids': strategic_voters,
                'new_winner': new_winner,
                'new_total_happiness': new_total_happiness,
                'individual_gains': individual_gains,
                'total_happiness_change': new_total_happiness - sum(honest_individual_happiness.values()),
                'strategic_preferences': dict(voter_preferences),
                'num_voters': len(strategic_voters),
                'collective_action_required': collective_action_required
            }
        return None
    
    def _is_effective_alone(self, situation, voter_id, voter_preferences, 
                             voting_scheme, happiness_func, honest_individual_happiness):
        """Test if a voter can achieve similar benefits by acting alone"""
        for vid, prefs in voter_preferences:
            if vid == voter_id:
                strategic_prefs = prefs
                break
        
        test_solo = deepcopy(situation)
        test_solo.voters[voter_id].preferences = strategic_prefs
        
        if happiness_func in [HappinessFunc.KENDALL_TAU, HappinessFunc.WEIGHTED_POSITIONAL]:
            new_ranking = self.schemes.apply_voting_scheme(voting_scheme, test_solo.voters, return_ranking=True)
            new_total_happiness, new_individual_happiness = self.happiness.calculate_ranked(
                situation.voters, new_ranking, happiness_func)
        else:
            new_winner = self.schemes.apply_voting_scheme(voting_scheme, test_solo.voters)
            new_total_happiness, new_individual_happiness = self.happiness.calculate(
                situation.voters, new_winner, happiness_func)
        
        old_happiness = honest_individual_happiness[voter_id]
        new_happiness = new_individual_happiness[voter_id]
        
        return new_happiness > old_happiness

    def analyse(self, situation, happiness_func, voting_scheme, strategy_type, verbose=False):
        """
        Analyze a situation considering multiple simultaneous strategic voters.
        Returns detailed analysis of strategic voting opportunities.
        """
        if happiness_func in [HappinessFunc.KENDALL_TAU, HappinessFunc.WEIGHTED_POSITIONAL]:
            honest_ranking = self.schemes.apply_voting_scheme(voting_scheme, situation.voters, return_ranking=True)
            honest_winner = honest_ranking[0]
            honest_total_happiness, honest_individual_happiness = self.happiness.calculate_ranked(
                situation.voters, honest_ranking, happiness_func)
        else:
            honest_winner = self.schemes.apply_voting_scheme(voting_scheme, situation.voters)
            honest_total_happiness, honest_individual_happiness = self.happiness.calculate(
                situation.voters, honest_winner, happiness_func)

        if verbose:
            print(f"\nHonest outcome analysis:")
            print(f"Winner: {honest_winner}")
            print(f"Total happiness: {honest_total_happiness:.3f}")
            for voter_id, happiness in honest_individual_happiness.items():
                print(f"Voter {voter_id}: {happiness:.3f}")

        all_voter_strategic_options = {}
        individual_opportunities = []
        
        for voter_index in range(len(situation.voters)):
            strategic_preferences = self.strategy.get_strategic_preferences_for_voter(
                situation, voter_index, voting_scheme, happiness_func, strategy_type, 
                exhaustive_search=True, verbose=False)
            if strategic_preferences:
                all_voter_strategic_options[voter_index] = strategic_preferences
                individual_opportunities.append(voter_index)

        multi_voter_opportunities = []
        for num_strategic_voters in range(2, min(self.max_strategic_voters + 1, len(situation.voters) + 1)):
            for voter_subset in itertools.combinations(range(len(situation.voters)), num_strategic_voters):
                if not any(v in all_voter_strategic_options for v in voter_subset):
                    continue
                voter_options = []
                for voter_id in voter_subset:
                    if voter_id in all_voter_strategic_options:
                        voter_options.append([(voter_id, prefs) for prefs in all_voter_strategic_options[voter_id]])
                    else:
                        voter_options.append([(voter_id, situation.voters[voter_id].preferences)])
                for combination in itertools.product(*voter_options):
                    result = self.evaluate_strategic_combination(
                        situation, combination, voting_scheme, happiness_func,
                        honest_winner, honest_individual_happiness
                    )
                    if result:
                        multi_voter_opportunities.append(result)

        has_individual = len(individual_opportunities) > 0
        has_multi_voter = len(multi_voter_opportunities) > 0

        if verbose:
            self._print_analysis_results(
                has_individual, has_multi_voter,
                individual_opportunities, multi_voter_opportunities,
                honest_winner, honest_total_happiness
            )

        return {
            'has_individual_strategic': has_individual,
            'has_multi_voter_strategic': has_multi_voter,
            'individual_opportunities': individual_opportunities,
            'multi_voter_opportunities': multi_voter_opportunities,
            'honest_winner': honest_winner,
            'honest_total_happiness': honest_total_happiness,
            'honest_individual_happiness': honest_individual_happiness
        }

    def _print_analysis_results(self, has_individual, has_multi_voter, 
                                individual_opps, multi_voter_opps, 
                                honest_winner, honest_happiness):
        print("\nStrategic Voting Analysis Results:")
        print(f"Individual strategic voting possible: {has_individual}")
        if has_individual:
            print(f"Voters with individual opportunities: {individual_opps}")
        print(f"Multi-voter strategic voting possible: {has_multi_voter}")
        if has_multi_voter:
            print("\nMulti-voter strategic opportunities:")
            for i, opp in enumerate(multi_voter_opps, 1):
                print(f"\nOpportunity {i}:")
                print(f"Voters involved: {opp['voter_ids']}")
                print(f"New winner: {opp['new_winner']}")
                for voter_id, gain in opp['individual_gains'].items():
                    print(f"  Voter {voter_id}: {gain:+.3f}")
                print(f"Total happiness change: {opp['total_happiness_change']:+.3f}")

    def analyse_multiple(self, num_repetitions, num_voters, num_candidates, voting_scheme, happiness_func, strategy_type, verbose=False):
        """
        Run multiple analyses to determine ATVA4 risk and happiness improvement.
        
        For each simulation, we compute the maximum number of voters that
        have a beneficial strategic option. Then:
        
            ATVA4 risk (%) = (sum(max_strategic_voters over simulations) / (num_repetitions * num_voters)) * 100
        
        And we compute the happiness improvement rate as the percentage of simulations
        where the best strategic total happiness exceeds the honest total happiness.
        """
        total_coalition_sum = 0
        beneficial_simulations = 0
        
        for _ in tqdm(range(num_repetitions), disable=not verbose):
            situation = Situation(num_voters=num_voters, num_candidates=num_candidates)
            result = self.analyse(situation, happiness_func, voting_scheme, strategy_type, verbose=False)
            
            if result['has_multi_voter_strategic']:
                max_coalition = max(len(opp['voter_ids']) for opp in result['multi_voter_opportunities'])
            elif result['has_individual_strategic']:
                max_coalition = 1
            else:
                max_coalition = 0
            total_coalition_sum += max_coalition
            
            best_strategic_total = max((opp['new_total_happiness'] for opp in result['multi_voter_opportunities']), default=result['honest_total_happiness'])
            if best_strategic_total > result['honest_total_happiness']:
                beneficial_simulations += 1
                
        atva4_risk = (total_coalition_sum / (num_repetitions * num_voters)) * 100
        happiness_improvement_rate = (beneficial_simulations / num_repetitions) * 100
        
        return {
            'atva4_risk': atva4_risk,
            'happiness_improvement_rate': happiness_improvement_rate
        }
