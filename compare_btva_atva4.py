from tva.models.ATVA4 import BTVA, ATVA4
from tva.situation import Situation
from tva.enums import VotingScheme, HappinessFunc, StrategyType
import pandas as pd
from tabulate import tabulate


def compare_btva_atva4():
    """Compare BTVA and ATVA4 results for strategic voting risk"""
    
    # Configuration
    num_repetitions = 1000  # Reduced for faster execution
    num_voters = 7
    num_candidates = 5
    max_simultaneous_voters = 4  # Maximum number of voters that can vote strategically simultaneously
    
    voting_schemes = [
        VotingScheme.PLURALITY,
        VotingScheme.VOTE_FOR_TWO,
        VotingScheme.ANTI_PLURALITY,
        VotingScheme.BORDA
    ]
    
    happiness_funcs = [
        HappinessFunc.LINEAR,
        HappinessFunc.LOG,
        HappinessFunc.EXP,
        HappinessFunc.KENDALL_TAU,
        HappinessFunc.WEIGHTED_POSITIONAL
    ]
    
    strategy_types = [
        StrategyType.BULLET,
        StrategyType.BURYING,
        StrategyType.COMPROMISING
    ]
    
    # Initialize models
    btva = BTVA()
    atva4 = ATVA4(max_simultaneous_voters)
    
    results = []
    
    print(f"Comparing BTVA and ATVA4 (max simultaneous voters: {max_simultaneous_voters})")
    print(f"Running {num_repetitions} simulations for each configuration")
    print(f"Number of voters: {num_voters}, Number of candidates: {num_candidates}")
    print("-" * 80)
    
    for voting_scheme in voting_schemes:
        print(f"\nVoting Scheme: {voting_scheme}")
        for happiness_func in happiness_funcs:
            print(f"\n  Happiness Function: {happiness_func}")
            for strategy_type in strategy_types:
                print(f"\n    Strategy Type: {strategy_type}")
                
                btva_risk = btva.analyse_multiple(
                    num_repetitions, num_voters, num_candidates, 
                    voting_scheme, happiness_func, strategy_type, False)
                
                atva4_result = atva4.analyse_multiple(
                    num_repetitions, num_voters, num_candidates, 
                    voting_scheme, happiness_func, strategy_type, False)
                
                results.append({
                    'voting_scheme': voting_scheme,
                    'happiness_func': happiness_func,
                    'strategy_type': strategy_type,
                    'btva_risk': btva_risk,
                    'atva4_risk': atva4_result['atva4_risk'],
                    'happiness_improvement_rate': atva4_result['happiness_improvement_rate']
                })
                
                print(f"      BTVA Risk:                 {btva_risk:.2f}%")
                print(f"      ATVA4 Risk:                {atva4_result['atva4_risk']:.2f}%")
                print(f"      Happiness Improvement:      {atva4_result['happiness_improvement_rate']:.2f}%")
    
    df = pd.DataFrame(results)
    df['voting_scheme'] = df['voting_scheme'].astype(str)
    df['happiness_func'] = df['happiness_func'].astype(str)
    df['strategy_type'] = df['strategy_type'].astype(str)
    
    print("\n=== Summary Statistics ===")
    
    # Average risks by voting scheme
    print("\nAverage Risks by Voting Scheme:")
    scheme_summary = df.groupby('voting_scheme').agg({
    'btva_risk': 'mean',
    'atva4_risk': 'mean',
    'happiness_improvement_rate': 'mean'
    }).round(2)
    print(tabulate(scheme_summary, headers='keys', tablefmt='grid'))
    
    # Average risks by happiness function
    print("\nAverage Risks by Happiness Function:")
    happiness_summary = df.groupby('happiness_func').agg({
    'btva_risk': 'mean',
    'atva4_risk': 'mean',
    'happiness_improvement_rate': 'mean'
    }).round(2)
    print(tabulate(happiness_summary, headers='keys', tablefmt='grid'))
    
    return df  # Return DataFrame for further analysis 

if __name__ == "__main__":
    # Run comparison and create DataFrame
    df = compare_btva_atva4()
    
    