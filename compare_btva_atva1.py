import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

from tva.models.ATVA1 import ATVA1
from tva.situation import Situation
from tva.enums import VotingScheme, HappinessFunc



def compare_btva_atva1_modified():
    """
    Compares ATVA1 risk under the BORDA voting scheme for different maximum colluder values,
    across two different happiness functions. Produces a DataFrame and plots the average risk
    versus max colluders.
    """
    # Configuration
    num_repetitions = 800 # Adjust as needed for execution time
    num_voters = 10
    num_candidates = 5
    max_collusion_values = list(range(2, 10))  # From 2 to 9 inclusive
    
    # We use only the BORDA scheme here
    voting_scheme = VotingScheme.BORDA
    
    # Define the happiness functions to compare
    happiness_funcs = [
        HappinessFunc.LINEAR,
        HappinessFunc.KENDALL_TAU
    ]
    
    atva1 = ATVA1()
    results = []
    
    print(f"Running {num_repetitions} simulations for each configuration")
    print(f"Number of voters: {num_voters}, Number of candidates: {num_candidates}")
    print("-" * 80)
    
    # Loop over happiness functions and max colluders values
    for happiness_func in happiness_funcs:
        print(f"\nHappiness Function: {happiness_func}")
        for max_c in max_collusion_values:
            print(f"  Testing with max colluders = {max_c}")
            # Generate simulation situations
            situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
            # Run analysis for current configuration
            analysis_result = atva1.analyse_multiple_ATVA(situations,num_repetitions, voting_scheme, happiness_func, max_collusion=max_c, verbose=False)
            avg_risk = analysis_result['atva1_risk']  # Assuming this key returns the average risk value
            results.append({
                'happiness_func': str(happiness_func),
                'max_colluders': max_c,
                'avg_risk': avg_risk
            })
    
    # Create DataFrame from the results
    df = pd.DataFrame(results)
    
    print("\n=== Summary Statistics ===")
    # Average risks by happiness function and max colluders
    summary = df.groupby(['happiness_func', 'max_colluders']).agg({'avg_risk': 'mean'}).reset_index()
    print(tabulate(summary, headers='keys', tablefmt='grid'))
    
    # Plotting the results
    plt.figure(figsize=(8, 6))
    for func in df['happiness_func'].unique():
        subset = df[df['happiness_func'] == func]
        plt.plot(subset['max_colluders'], subset['avg_risk'], marker='o', label=func)
    plt.xlabel('Max Colluders')
    plt.ylabel('Average Risk')
    plt.title('Average Risk vs. Max Colluders (Borda Scheme)')
    plt.legend(title='Happiness Function')
    plt.grid(True)
    plt.show()
    
    return df
def compare_schemes_kendall_tau():
    """
    Compares ATVA1 risk across multiple voting schemes using the Kendall Tau happiness function,
    for a range of max colluders (from 2 to 9). Produces a DataFrame and a plot with:
      - x-axis: Max Colluders
      - y-axis: Average Risk
    """
    # Configuration
    num_repetitions = 800  # Adjust as needed
    num_voters = 10
    num_candidates = 5
    max_collusion_values = list(range(2, 10))  # From 2 to 9 inclusive

    # Define the voting schemes to compare
    voting_schemes = [
        VotingScheme.PLURALITY,
        VotingScheme.VOTE_FOR_TWO,
        VotingScheme.ANTI_PLURALITY,
        VotingScheme.BORDA
    ]
    
    # Fixed happiness function: Kendall Tau
    happiness_func = HappinessFunc.KENDALL_TAU
    
    atva1 = ATVA1()
    results = []
    
    print(f"Running {num_repetitions} simulations for each configuration")
    print(f"Number of voters: {num_voters}, Number of candidates: {num_candidates}")
    print("-" * 80)
    
    for scheme in voting_schemes:
        print(f"\nVoting Scheme: {scheme}")
        for max_c in max_collusion_values:
            print(f"  Testing with max colluders = {max_c}")
            # Generate simulation situations for each configuration
            situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
            # Run analysis for current voting scheme and max colluders value
            analysis_result = atva1.analyse_multiple_ATVA(situations,num_repetitions, scheme, happiness_func, max_collusion=max_c, verbose=False)
            avg_risk = analysis_result['atva1_risk']  # Retrieve the average risk
            results.append({
                'voting_scheme': str(scheme),
                'max_colluders': max_c,
                'avg_risk': avg_risk
            })
    
    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    # Grouping and printing summary statistics
    summary = df.groupby(['voting_scheme', 'max_colluders']).agg({'avg_risk': 'mean'}).reset_index()
    print("\n=== Summary Statistics ===")
    print(tabulate(summary, headers='keys', tablefmt='grid'))
    
    # Plot the results
    plt.figure(figsize=(8, 6))
    for scheme in df['voting_scheme'].unique():
        subset = df[df['voting_scheme'] == scheme]
        plt.plot(subset['max_colluders'], subset['avg_risk'], marker='o', label=scheme)
    plt.xlabel('Max Colluders')
    plt.ylabel('Average Risk')
    plt.title('Average Risk vs. Max Colluders (Happiness: Kendall Tau)')
    plt.legend(title='Voting Scheme')
    plt.grid(True)
    plt.show()
    
    return df


if __name__ == "__main__":
    df_result = compare_btva_atva1_modified()
    #df_result = compare_schemes_kendall_tau()
    df_result.to_csv('atva1happ.csv')
