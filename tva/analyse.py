from situation import Situation
from schemes import Schemes
from globals import *

# Create the voting situation
situation = Situation()

# Apply the voting scheme to the situation
schemes = Schemes(situation.preference_matrix)
winner = schemes.plurality_voting()

