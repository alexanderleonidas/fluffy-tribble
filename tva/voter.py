import random

class Voter:
    def __init__(self, voter_id, candidates):
        self.voter_id = voter_id
        self.preferences = self.get_preferences(candidates)

    @staticmethod
    def get_preferences(c):
        # Shuffles the candidate list
        return random.sample(c, len(c))

    # TODO: implement voter happiness