from enum import Enum


# Enum class for voting schemes
class VotingScheme(Enum):
    PLURALITY = 'PLURALITY'
    VOTE_FOR_TWO = 'VOTE FOR TWO'
    ANTI_PLURALITY = 'ANTI PLURALITY'
    BORDA = 'BORDA'

# Enum class for happiness functions
class HappinessFunc(Enum):
    LOG = 'LOGARITHMIC'
    EXP = 'EXPONENTIAL'
    LINEAR = 'LINEAR'
    KENDALL_TAU = 'KENDALL TAU DISTANCE'
    WEIGHTED_POSITIONAL = 'WEIGHTED POSITIONAL'

class StrategyType(Enum):
    COMPROMISING = 'COMPROMISING'
    BURYING = 'BURYING'
    BULLET = 'BULLET'