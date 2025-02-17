from enum import Enum

# Enum class for voting schemes
class VotingScheme(Enum):
    PLURALITY = 1
    VOTE_FOR_TWO = 2
    ANTI_PLURALITY = 3
    BORDA = 4

# Enum class for happiness functions
class Happiness(Enum):
    LOG = 1
    EXP = 2
    LINEAR = 3