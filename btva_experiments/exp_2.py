import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os
from tva.models.BTVA import BTVA
from tva.enums import StrategyType, VotingScheme, HappinessFunc
from tva.situation import Situation

# Experiment settings
num_repetitions = 25
num_candidates = 5
voter_range = range(3, 51)
voting_schemes = [VotingScheme.PLURALITY, VotingScheme.VOTE_FOR_TWO, VotingScheme.ANTI_PLURALITY, VotingScheme.BORDA]
happiness_func = HappinessFunc.KENDALL_TAU
strategy_type = StrategyType.COMPROMISING

title = f"{num_candidates} candidates, {happiness_func.value.lower()}, {strategy_type.value.lower()}"
results_file = title + ' step 2.csv'

if not os.path.exists(results_file):


    btva = BTVA()

    # Store results for strategic voting
    strategic_results = []

    for voting_scheme in voting_schemes:
        for num_voters in voter_range:
            situations = [Situation(num_voters, num_candidates) for _ in range(num_repetitions)]
            risk, avg_strategic_happiness, avg_honest_happiness = btva.analyse_multiple(situations, voting_scheme, happiness_func, strategy_type, return_avg_happiness=True, verbose=False)
            # avg_strategic_happiness = total_strategic_happiness / num_repetitions
            strategic_results.append((num_voters, voting_scheme.value, avg_honest_happiness, avg_strategic_happiness, risk))

    # Convert results to DataFrame
    strategic_df = pd.DataFrame(strategic_results, columns=["num_voters", "voting_scheme", "avg_honest_happiness", "avg_strategic_happiness", "risk"])
    strategic_df.to_csv(title)

else:
    strategic_df = pd.read_csv(results_file)

# Plot results
plt.figure(figsize=(12, 8))
for voting_scheme in voting_schemes:
    subset = strategic_df[strategic_df["voting_scheme"] == voting_scheme.value]
    plt.plot(subset["num_voters"], subset["avg_honest_happiness"], label=f"{voting_scheme.value} - Honest")
    plt.plot(subset["num_voters"], subset["avg_strategic_happiness"], linestyle='--', label=f"{voting_scheme.value} - Strategic")

plt.xlabel("Number of Voters")
plt.ylabel("Average Total Happiness")
plt.title("Average Voter Happiness under Honest and Strategic Voting")
plt.legend()
plt.grid(True)
plt.show()


### Step 3 ####
# Calculate differences between honest and strategic happiness
strategic_df["happiness_difference"] = strategic_df["avg_strategic_happiness"] - strategic_df["avg_honest_happiness"]

# Plot happiness difference
plt.figure(figsize=(12, 8))
for voting_scheme in voting_schemes:
    subset = strategic_df[strategic_df["voting_scheme"] == voting_scheme.value]
    plt.plot(subset["num_voters"], subset["happiness_difference"], label=voting_scheme.value)

plt.xlabel("Number of Voters")
plt.ylabel("Happiness Difference (Strategic - Honest)")
plt.title("Impact of Strategic Voting on Total Happiness")
plt.legend()
plt.grid(True)
plt.show()

### Visualisation

# Heatmaps of strategic impact
heatmap_data = strategic_df.pivot(index="num_voters", columns="voting_scheme", values="happiness_difference")
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, cmap="coolwarm")
plt.xlabel("Voting Scheme")
plt.ylabel("Number of Voters")
plt.title("Heatmap of Strategic Voting Impact")
plt.show()

# Scatter plots of tactical-voting risk vs. voter happiness
plt.figure(figsize=(12, 8))
sns.scatterplot(data=strategic_df, x="risk", y="avg_honest_happiness", hue="voting_scheme")
plt.xlabel("Happiness Difference (Strategic - Honest)")
plt.ylabel("Average Honest Happiness")
plt.title("Tactical-Voting Risk vs. Voter Happiness")
plt.show()