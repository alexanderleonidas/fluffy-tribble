import math
from tva.enums import HappinessFunc
from tva.voter import Voter

class Happiness:

  def calculate(self, preference_matrix:list[Voter], winner:str, happiness_func:HappinessFunc):
      total_happiness = 0.0
      individual_happiness = {}
      for voter in preference_matrix:
          score = self.calculate_individual(voter.preferences, winner, happiness_func)
          individual_happiness[voter.voter_id] = score
          total_happiness += score # type: ignore
      return total_happiness, individual_happiness

  def calculate_individual(self, preference, winner: str, happiness_func: HappinessFunc):
      """ Apply the specified voting scheme to determine the winner. """
      if happiness_func == HappinessFunc.LOG:
          return self.__logarithmic_happiness(preference, winner)
      elif happiness_func == HappinessFunc.EXP:
          return self.__exponential_happiness(preference, winner)
      # elif happiness_func == HappinessFunc.LINEAR:
      return self.__linear_happiness(preference, winner)

  @staticmethod
  def __logarithmic_happiness(preferences:list, winner: str):
      """
      A logarithmic decay hapiness function.
      If the winning candidate is ranked r (1-indexed),
        H_i = 1 / log2(r + 1)
      so that a voter whose top candidate wins (r = 1) gets happiness 1.
      """
      r = preferences.index(winner) + 1  # convert to 1-index
      return 1 / math.log2(r + 1)

  @staticmethod
  def __exponential_happiness(preferences:list, winner: str, decay_alpha=0.5):
      """
      An exponential decay happiness function.
      Here we use a “shift” so that if the winner is a voter's top choice (r = 1),
        H_i = exp(-alpha*(1-1)) = exp(0) = 1.
      For lower-ranked outcomes, happiness decays as:
        H_i = exp(-alpha*(r-1))
      """
      r = preferences.index(winner) + 1
      return math.exp(-decay_alpha * (r - 1))

  @staticmethod
  def __linear_happiness(preferences:list, winner: str):
      """
      A normalized linear score happiness function.
      If there are m candidates and the winner is at rank r (1-indexed),
        H_i = (m - r) / (m - 1)
      so that a top-ranked candidate gives H_i = 1 and the last-ranked gives H_i = 0.
      """
      m = len(preferences)  # Number of candidates
      r = preferences.index(winner) + 1 if winner in preferences else 0
      return (m - r) / (m - 1) if m > 1 else 1.0