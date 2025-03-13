import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from tva.enums import VotingScheme, StrategyType, HappinessFunc
from tva.models.BTVA import BTVA
from tva.situation import Situation

# Experiment settings
num_repetitions = 1000
voter_range = range(3, 51)  # Vary num_voters
candidate_range = range(3, 11)  # Vary num_candidates
voting_scheme = VotingScheme.BORDA
strategy_type = StrategyType.COMPROMISING
happiness_func = HappinessFunc.KENDALL_TAU
verbose = False

# File to store results
title = f"{voting_scheme.value.lower()} voting, {strategy_type.value.lower()} strategy, {happiness_func.value.lower()}"
results_file = title + ' results.csv'

# Load existing results if the file exists
if os.path.exists(results_file):
    existing_results = pd.read_csv(results_file)
    if not existing_results.empty:
        last_voter = existing_results.num_voters.iloc[-1]
        last_candidate = existing_results.num_candidates.iloc[-1]
        print(f"Resuming experiment from last completed: num_voters={last_voter}, num_candidates={last_candidate}")
        X = existing_results.num_voters.tolist()
        Y = existing_results.num_candidates.tolist()
        Z = existing_results.risk.tolist()
else:
    existing_results = pd.DataFrame(columns=["num_voters", "num_candidates", "risk"])
    existing_results.to_csv(results_file, index=False)
    X, Y, Z = [], [], []

# Initialize BTVA
btva = BTVA()

# Convert existing results to a set for quick lookup
completed_experiments = set(zip(existing_results.num_voters, existing_results.num_candidates))

# Run experiments across varying num_voters and num_candidates
for num_voters in voter_range:
    for num_candidates in candidate_range:
        if (num_voters, num_candidates) in completed_experiments:
            continue  # Skip already completed experiments

        situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
        risk = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, verbose)

        # Save iteration results immediately
        result_df = pd.DataFrame([[num_voters, num_candidates, risk]], columns=["num_voters", "num_candidates", "risk"])
        result_df.to_csv(results_file, mode='a', header=False, index=False)

        # Store for plotting
        X.append(num_voters)
        Y.append(num_candidates)
        Z.append(risk)

# Convert lists to NumPy arrays for plotting
X, Y, Z = np.array(X), np.array(Y), np.array(Z)

# Create 3D plot
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(X, Y, Z, cmap='viridis', edgecolor='black')

# Labels and Title
ax.set_xlabel("Number of Voters")
ax.set_ylabel("Number of Candidates")
ax.set_zlabel("Risk")
ax.set_title(title)

plt.show()
