import random
import numpy as np

class Voter:
    def __init__(self, voter_id, candidates, seed=None):
        self.voter_id = voter_id
        self.rng = random.Random(seed)
        self.preferences = self.get_preferences(candidates)

    def get_preferences(self, c):
        # Shuffles the candidate list using random.Random with a seed
        indices = list(range(len(c)))
        self.rng.shuffle(indices)
        return [c[i] for i in indices]

    def __repr__(self):
        return f'Voter {self.voter_id}: {self.preferences}'

    # TODO: implement voter happiness
    def happiness(self, winner):
        # Calculate the happiness of the voter based on the winner
        # The happiness is the position of the winner in the voter's preference list
        return len(self.preferences) - self.preferences.index(winner)
    
voter = Voter(1, ['A', 'B', 'C', 'D'], seed=42)
# print(voter)
# print(voter.happiness('A'))

