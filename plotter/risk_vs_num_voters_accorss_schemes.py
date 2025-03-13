import pandas as pd
import matplotlib.pyplot as plt
from tva.enums import VotingScheme, StrategyType, HappinessFunc
from tva.models.BTVA import BTVA
import os
from tva.situation import Situation

# Experiment settings
num_repetitions = 1000
num_candidates = 5  # Fixed number of candidates
voter_range = range(3, 101)  # Vary number of voters
strategy_type = StrategyType.COMPROMISING
happiness_func = HappinessFunc.KENDALL_TAU
verbose = False

# Define voting schemes to test
voting_schemes = {
    "PLURALITY": VotingScheme.PLURALITY,
    "VOTE_FOR_TWO": VotingScheme.VOTE_FOR_TWO,
    "ANTI_PLURALITY": VotingScheme.ANTI_PLURALITY,
    "BORDA": VotingScheme.BORDA
}

# File to store results
title = f"{num_candidates} candidates, {strategy_type.value.lower()} strategy, {happiness_func.value.lower()}"
results_file = title + ' results.csv'
# Load existing results if the file exists
if os.path.exists(results_file):
    existing_results = pd.read_csv(results_file)
    if not existing_results.empty:
        last_voter = existing_results.num_voters.iloc[-1]
        last_scheme = existing_results.voting_scheme.iloc[-1]
        print(f"Resuming experiment from last completed: num_voters={last_voter}, scheme={last_scheme}")
else:
    existing_results = pd.DataFrame(columns=["num_voters", "voting_scheme", "risk"])
    existing_results.to_csv(results_file, index=False)

# Initialize BTVA
btva = BTVA()

# Convert existing results to a set for quick lookup
completed_experiments = set(zip(existing_results.num_voters, existing_results.voting_scheme))

# Plot setup
plt.figure(figsize=(10, 6))

# Run experiments for each voting scheme
for label, voting_scheme in voting_schemes.items():
    risks = []  # Store risk values for this scheme
    for num_voters in voter_range:
        if (num_voters, label) in completed_experiments:
            continue  # Skip already completed experiments

        situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
        risk = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, verbose)

        # Save iteration results immediately
        result_df = pd.DataFrame([[num_voters, label, risk]], columns=["num_voters", "voting_scheme", "risk"])
        result_df.to_csv(results_file, mode='a', header=False, index=False)

        # Store for plotting
        risks.append(risk)
        print('Risk: ', risk)

    # Plot results
    plt.plot(voter_range[:len(risks)], risks, label=label, marker='o', linestyle='-')

# Graph styling
plt.xlabel("Number of Voters")
plt.ylabel("Risk")
plt.title(title)
plt.legend()
plt.grid(True)
plt.show()
