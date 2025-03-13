import matplotlib.pyplot as plt
import pandas as pd
import os
from tva.enums import VotingScheme, StrategyType, HappinessFunc
from tva.models.BTVA import BTVA
from tva.situation import Situation

# Experiment settings
num_repetitions = 1000
num_candidates = 6  # Keeping candidates constant
voter_range = range(3, 101)  # Vary the number of voters
voting_scheme = VotingScheme.PLURALITY
strategy_type = StrategyType.COMPROMISING
verbose = False

# Define happiness functions to test
happiness_functions = {
    "LINEAR": HappinessFunc.LINEAR,
    "KENDALL_TAU": HappinessFunc.KENDALL_TAU
}

# File to store results
title = f"{num_candidates} candidates, {strategy_type.value.lower()} strategy, {voting_scheme.value.lower()} scheme"
results_file = title + ' results.csv'

# Load existing results if the file exists
if os.path.exists(results_file):
    existing_results = pd.read_csv(results_file)
    if not existing_results.empty:
        last_voter = existing_results.num_voters.iloc[-1]
        last_happiness_func = existing_results.happiness_func.iloc[-1]
        print(f"Resuming experiment from last completed: num_voters={last_voter}, happiness_func={last_happiness_func}")
else:
    existing_results = pd.DataFrame(columns=["num_voters", "happiness_func", "risk"])
    existing_results.to_csv(results_file, index=False)

# Initialize BTVA
btva = BTVA()

# Convert existing results to a set for quick lookup
completed_experiments = set(zip(existing_results.num_voters, existing_results.voting_scheme))

# Plot setup
plt.figure(figsize=(10, 6))

# Run experiments for each happiness function
for label, happiness_func in happiness_functions.items():
    risks = []  # Store risk values for this function
    for num_voters in voter_range:
        if (num_voters, label) in completed_experiments:
            continue  # Skip already completed experiments

        situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
        risk = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, verbose)
        risks.append(risk)

        # Save iteration results immediately
        result_df = pd.DataFrame([[num_voters, label, risk]], columns=["num_voters", "happiness_func", "risk"])
        result_df.to_csv(results_file, mode='a', header=False, index=False)

    # Plot results
    plt.plot(voter_range, risks, label=label, marker='o', linestyle='-')

# Graph styling
plt.xlabel("Number of Voters")
plt.ylabel("Risk")
plt.title(title)
plt.legend()
plt.grid(True)
plt.show()