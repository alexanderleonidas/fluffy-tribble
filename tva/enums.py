from enum import Enum
# Create an enum with every type of voting
class VotingScheme(Enum):
    PLURALITY = 1
    VOTE_FOR_TWO = 2
    ANTI_PLURALITY = 3
    BORDA = 4