from copy import deepcopy
from tva.situation import Situation
from tva.enums import HappinessFunc, VotingScheme, StrategyType
from BTVA import BTVA
import random

class ATVA2(BTVA):
    def __init__(self):
        BTVA.__init__(self)

    