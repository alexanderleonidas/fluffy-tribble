import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from tva.enums import VotingScheme, HappinessFunc
from tva.models.BTVA import BTVA
from tva.situation import Situation

# Experiment settings
num_repetitions = 50
num_candidates = 5
voter_range = range(3, 51)
voting_schemes = [VotingScheme.PLURALITY, VotingScheme.VOTE_FOR_TWO, VotingScheme.ANTI_PLURALITY, VotingScheme.BORDA]
happiness_func = HappinessFunc.LINEAR


title = f"{num_candidates} candidates, {happiness_func.value.lower()}, "
results_file = title + ' step 1.csv'

# Initialize BTVA
btva = BTVA()

# Store results
results = []

for voting_scheme in voting_schemes:
    for num_voters in voter_range:
        situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
        total_happiness = 0
        for situation in situations:
            total_h, _ = situation.calculate_happiness(situation.voters, happiness_func, voting_scheme)
            total_happiness += total_h
        avg_happiness = total_happiness / num_repetitions
        results.append((num_voters, voting_scheme.value, avg_happiness))

# Convert results to DataFrame
df = pd.DataFrame(results, columns=["num_voters", "voting_scheme", "avg_happiness"])
df.to_csv(results_file, mode='a', header=False, index=False)

# Plot results
plt.figure(figsize=(12, 8))
for voting_scheme in voting_schemes:
    subset = df[df["voting_scheme"] == voting_scheme.value]
    plt.plot(subset["num_voters"], subset["avg_happiness"], label=voting_scheme.value)

plt.xlabel("Number of Voters")
plt.ylabel("Average Happiness")
plt.title(title)
plt.legend()
plt.grid(True)
plt.show()

# Histograms of voter happiness
plt.figure(figsize=(12, 8))
sns.histplot(data=df, x="avg_happiness", hue="voting_scheme", multiple="stack", kde=True)
plt.xlabel("Average Happiness")
plt.ylabel("Frequency")
plt.title("Histogram of " + title)
plt.show()