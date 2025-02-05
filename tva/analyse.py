from situation import Situation
from schemes import Schemes
from globals import *

# Create the voting situation
situation = Situation()

# Apply the voting scheme to the situation
schemes = Schemes(situation.preference_matrix)
print(situation.preference_matrix)
winner1 = schemes.anti_plurality_voting()
winner2 = schemes.voting_for_two()
winnner3 = schemes.borda_voting()
print("Anti plurality:",winner1,", Two voting:", winner2, ", Borda:", winnner3)

