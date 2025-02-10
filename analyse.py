from tva.situation import Situation
from tva.schemes import Schemes

# Create the voting situation
situation = Situation(num_voters=4, num_candidates=4, seed=42)

# Apply the voting scheme to the situation
schemes = Schemes()
print(situation)
winner1 = schemes.anti_plurality_voting(situation.voters)
winner2 = schemes.voting_for_two(situation.voters)
winnner3 = schemes.borda_voting(situation.voters)
print("Anti plurality:",winner1,", Two voting:", winner2, ", Borda:", winnner3)

