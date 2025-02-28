from enum import Enum


# Enum class for voting schemes
class VotingScheme(Enum):
    PLURALITY = 'PLURALITY'
    VOTE_FOR_TWO = 'VOTE FOR TWO'
    ANTI_PLURALITY = 'ANTI PLURALITY'
    BORDA = 'BORDA'

    def __str__(self):
        return self.value

# Enum class for happiness functions
class HappinessFunc(Enum):
    LOG = 'LOGARITHMIC'
    EXP = 'EXPONENTIAL'
    LINEAR = 'LINEAR'
    KENDALL_TAU = 'KENDALL TAU DISTANCE'
    WEIGHTED_POSITIONAL = 'WEIGHTED POSITIONAL'

    def __str__(self):
        return self.value

class StrategyType(Enum):
    COMPROMISING = 'COMPROMISING'
    BURYING = 'BURYING'
    BULLET = 'BULLET'

    def __str__(self):
        return self.value