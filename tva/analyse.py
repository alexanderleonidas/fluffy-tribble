from situation import Situation
from schemes import Schemes

# Example Usage

# Create the voting situation
situation = Situation()

situation.print_preference_matrix()
situation.strategies.compromising()
situation.print_preference_matrix()
# Apply different Schemes
winner1 = situation.schemes.anti_plurality_voting()
winner2 = situation.schemes.voting_for_two()
winner3 = situation.schemes.borda_voting()
print(winner1, winner2, winner3)

