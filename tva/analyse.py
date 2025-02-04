from situation import Situation
from schemes import Schemes

# Example Usage

# Create the voting situation
situation = Situation()

situation.print_preference_matrix()
print('Apply Compromising Strategy')
situation.strategies.compromising()
situation.print_preference_matrix()

# Apply different Schemes
winner1 = situation.schemes.plurality_voting()
winner2 = situation.schemes.anti_plurality_voting()
winner3 = situation.schemes.voting_for_two()
winner4 = situation.schemes.borda_voting()
print('Plurality Voting Winner: ', winner1)
print('Anti Plurality Voting Winner: ', winner2)
print('Voting for Two Winner: ', winner3)
print('Borda Voting Winner: ', winner4)

