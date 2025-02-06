# strategies.py
import copy
from globals import *
from random import sample


class Strategies:
    def __init__(self, preference_matrix):
        self.preference_matrix = preference_matrix
        self.num_strategic = NUM_STRATEGIC_VOTERS
        # Randomly select the indices of voters that will vote strategically.
        self.strategic_voter_ids = sample(range(0, len(self.preference_matrix)), self.num_strategic)


    def compromising(self):
        """A voter ranks an alternative insincerely higher than another (compromising move)."""
        for voter in self.preference_matrix:
            if voter.id in self.strategic_voter_ids:
                # Swap the first and second candidates.
                voter.preferences[0], voter.preferences[1] = voter.preferences[1], voter.preferences[0]

    def burying(self):
        """A voter ranks an alternative insincerely lower than another (burying move)."""
        for voter in self.preference_matrix:
            if voter.id in self.strategic_voter_ids:
                # Swap the penultimate and last candidates.
                voter.preferences[-2], voter.preferences[-1] = voter.preferences[-1], voter.preferences[-2]

    def get_strategic_options(self, schemes_instance,
                              scheme_types=["plurality", "anti_plurality", "voting_for_two", "borda"]):
        """
        For each strategic voter, generate one tactical option for each voting scheme provided in scheme_types.
        The tactical option is created by swapping the candidate at position 0 with the candidate at position 2
        (if there are at least 3 candidates; otherwise, swap the first and last candidates).

        For each scheme, the tactical option is a dictionary containing:
          - "modified_preferences": the altered preference list (tilde_v_ij)
          - "voting_outcome": outcome under the tactical vote (tilde_O)
          - "modified_voter_happiness": H_i after the tactical vote (tilde_H_i)
          - "original_voter_happiness": H_i for the non-strategic vote
          - "modified_overall_happiness": overall happiness after tactical vote (tilde_H)
          - "original_overall_happiness": overall non-strategic happiness (H)

        Returns:
          A list (one element per voter). For each strategic voter, the element is a dictionary with keys corresponding
          to each scheme type and values equal to the tactical option dictionary. For non-strategic voters, an empty dictionary is returned.
        """
        # Mapping from scheme name to method names.
        method_mapping = {
            "plurality": {
                "voting": "plurality_voting",
                "happiness": "plurality_happiness"
            },
            "anti_plurality": {
                "voting": "anti_plurality_voting",
                "happiness": "anti_plurality_happiness"
            },
            "voting_for_two": {
                "voting": "voting_for_two",  # note: method is named "voting_for_two"
                "happiness": "voting_for_two_happiness"
            },
            "borda": {
                "voting": "borda_voting",
                "happiness": "borda_happiness"
            }
        }

        # Compute the baseline (non-strategic) outcome and happiness for each scheme.
        original_results = {}
        for scheme in scheme_types:
            vote_method = getattr(schemes_instance, method_mapping[scheme]["voting"])
            happiness_method = getattr(schemes_instance, method_mapping[scheme]["happiness"])
            original_outcome = vote_method()
            original_happiness = happiness_method(original_outcome)
            original_overall_happiness = schemes_instance.overall_happiness(original_happiness)
            original_results[scheme] = {
                "outcome": original_outcome,
                "happiness": original_happiness,
                "overall": original_overall_happiness
            }

        strategic_options = []
        for i, voter in enumerate(self.preference_matrix):
            voter_options = {}
            if voter.id in self.strategic_voter_ids:
                for scheme in scheme_types:
                    # Create a deep copy of the preference matrix.
                    new_pref_matrix = copy.deepcopy(self.preference_matrix)
                    modified_voter = new_pref_matrix[i]
                    modified_preferences = modified_voter.preferences[:]  # Copy the list.

                    # Tactical modification: swap candidate at index 0 with index 2 if possible.
                    if len(modified_preferences) > 2:
                        modified_preferences[0], modified_preferences[2] = modified_preferences[2], \
                        modified_preferences[0]
                    else:
                        modified_preferences[0], modified_preferences[-1] = modified_preferences[-1], \
                        modified_preferences[0]
                    modified_voter.preferences = modified_preferences

                    # Create a temporary Schemes instance using the modified preference matrix.
                    from schemes import Schemes
                    temp_schemes = Schemes(new_pref_matrix)

                    # Dynamically get the modified outcome and happiness methods.
                    mod_vote_method = getattr(temp_schemes, method_mapping[scheme]["voting"])
                    mod_happiness_method = getattr(temp_schemes, method_mapping[scheme]["happiness"])
                    modified_outcome = mod_vote_method()
                    modified_happiness = mod_happiness_method(modified_outcome)
                    modified_overall_happiness = temp_schemes.overall_happiness(modified_happiness)

                    option = {
                        "modified_preferences": modified_preferences,
                        "voting_outcome": modified_outcome,
                        "modified_voter_happiness": modified_happiness.get(voter.id, None),
                        "original_voter_happiness": original_results[scheme]["happiness"].get(voter.id, None),
                        "modified_overall_happiness": modified_overall_happiness,
                        "original_overall_happiness": original_results[scheme]["overall"]
                    }
                    voter_options[scheme] = option
            # Append an empty dictionary for non-strategic voters.
            strategic_options.append(voter_options)
        return strategic_options

    def compute_strategic_risk(self, strategic_options, num_voters):
        """
        Compute the overall risk of strategic voting as follows.
        For each tactical option (for each scheme), compute:
          - Overall risk: R_overall = max{0, (H - tilde_H) / H}
          - Individual risk: R_indiv = max{0, (H_i - tilde_H_i) / H_i}
        Then combine them with weights (alpha and beta, e.g., 0.5 each):
          risk_ij = alpha * R_overall + beta * R_indiv

        Finally, define the overall risk as:
          Overall Risk = (fraction of voters with at least one tactical option) * (average risk over all tactical options)
        """
        risk_values = []
        alpha = 0.3
        beta = 0.3

        for voter_options in strategic_options:
            for option in voter_options.values():
                orig_H = option["original_overall_happiness"]
                mod_H = option["modified_overall_happiness"]
                risk_overall = max(0, (orig_H - mod_H) / orig_H)

                orig_H_i = option["original_voter_happiness"]
                mod_H_i = option["modified_voter_happiness"]
                risk_indiv = max(0, (orig_H_i - mod_H_i) / orig_H_i) if orig_H_i != 0 else 0

                risk_option = alpha * risk_overall + beta * risk_indiv
                risk_values.append(risk_option)

        if risk_values:
            average_risk = sum(risk_values) / len(risk_values)
        else:
            average_risk = 0.0

        fraction_voters_with_options = sum(1 for options in strategic_options if options) / num_voters
        overall_risk = fraction_voters_with_options * average_risk
        return overall_risk
