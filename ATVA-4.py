from BTVA import BTVA
from tva.enums import HappinessFunc, VotingScheme, StrategyType
from tva.situation import Situation


class ATVA4(BTVA):
    def __init__(self):
        BTVA.__init__(self)

    def analyse(self, situation: Situation, happiness_func: HappinessFunc, voting_scheme: VotingScheme, strategy_type: StrategyType):
        pass