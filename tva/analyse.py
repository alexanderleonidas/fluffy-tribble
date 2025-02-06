from situation import Situation
from schemes import Schemes
from globals import *

# Create the voting situation
situation = Situation(num_voters=4, num_candidates=4, seed=42)

# Apply the voting scheme to the situation
schemes = Schemes()
print(situation.preference_matrix)
winner1 = schemes.anti_plurality_voting(situation.preference_matrix)
winner2 = schemes.voting_for_two(situation.preference_matrix)
winnner3 = schemes.borda_voting(situation.preference_matrix)
print("Anti plurality:",winner1,", Two voting:", winner2, ", Borda:", winnner3)

