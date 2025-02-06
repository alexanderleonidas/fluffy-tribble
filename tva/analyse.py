# analyse.py
import copy
from situation import Situation


def run_voting_schemes(situation, strategy_name):
    """
    For a given situation and strategy label, run the voting schemes and print:
      1. Non-strategic voting outcome (O)
      2. For each voter i, his/her happiness level (H_i)
      3. Overall voter happiness (H)
      4. For each voter i, the set S_i of strategic voting options
         (each option printed as a tuple: (tilde_v_ij, tilde_O, tilde_H_i, H_i, tilde_H, H))
      5. Overall risk of strategic voting.
    """
    print("======== {} Strategy Results ========".format(strategy_name))
    schemes = situation.schemes
    strategies = situation.strategies

    # Helper to print a scheme's results.
    def print_scheme_output(scheme_name, winner, happiness, overall_happiness):
        print("\n--- {} Voting ---".format(scheme_name))
        print("Non-strategic voting outcome (O):", winner)
        print("For each voter i, happiness level (H_i):", happiness)
        print("Overall voter happiness (H):", overall_happiness)

    # Plurality Voting:
    winner_plurality = schemes.plurality_voting()
    happiness_plurality = schemes.plurality_happiness(winner_plurality)
    overall_happiness_plurality = schemes.overall_happiness(happiness_plurality)
    print_scheme_output("Plurality", winner_plurality, happiness_plurality, overall_happiness_plurality)

    # Anti-Plurality Voting:
    winner_anti_plurality = schemes.anti_plurality_voting()
    happiness_anti_plurality = schemes.anti_plurality_happiness(winner_anti_plurality)
    overall_happiness_anti_plurality = schemes.overall_happiness(happiness_anti_plurality)
    print_scheme_output("Anti-Plurality", winner_anti_plurality, happiness_anti_plurality,
                        overall_happiness_anti_plurality)

    # Voting-for-Two Voting:
    winner_voting_for_two = schemes.voting_for_two()
    happiness_voting_for_two = schemes.voting_for_two_happiness(winner_voting_for_two)
    overall_happiness_voting_for_two = schemes.overall_happiness(happiness_voting_for_two)
    print_scheme_output("Voting-for-Two", winner_voting_for_two, happiness_voting_for_two,
                        overall_happiness_voting_for_two)

    # Borda Voting:
    winner_borda = schemes.borda_voting()
    happiness_borda = schemes.borda_happiness(winner_borda)
    overall_happiness_borda = schemes.overall_happiness(happiness_borda)
    print_scheme_output("Borda", winner_borda, happiness_borda, overall_happiness_borda)

    # Get strategic options dynamically for all schemes.
    strategic_options = strategies.get_strategic_options(schemes)
    print("\n--- Strategic Voting Options (S_i) ---")
    for i, voter_options in enumerate(strategic_options):
        voter_num = i + 1
        print("\nFor voter {}: S_{} = ".format(voter_num, voter_num))
        if voter_options:
            for scheme, option in voter_options.items():
                print("  Scheme:", scheme)
                print("    s_ij = (")
                print("         tilde_v_ij (modified_preferences):", option["modified_preferences"])
                print("         tilde_O (voting_outcome):", option["voting_outcome"])
                print("         tilde_H_i (modified_voter_happiness):", option["modified_voter_happiness"])
                print("         H_i (original_voter_happiness):", option["original_voter_happiness"])
                print("         tilde_H (modified_overall_happiness):", option["modified_overall_happiness"])
                print("         H (original_overall_happiness):", option["original_overall_happiness"])
                print("    )")
        else:
            print("    S_{} is empty.".format(voter_num))

    num_voters = len(situation.preference_matrix)
    strat_voting_risk = strategies.compute_strategic_risk(strategic_options, num_voters)
    print("\nOverall risk of strategic voting:", strat_voting_risk)


def main():
    # Create the initial voting situation.
    situation = Situation()
    print("=== Initial Voting Situation ===")
    situation.print_preference_matrix()

    # Create deep copies for different strategies.
    situation_compromising = copy.deepcopy(situation)
    situation_burying = copy.deepcopy(situation)

    # Compromising Strategy:
    situation_compromising.strategies.compromising()
    print("\n=== After Strategic (Compromising) Adjustment ===")
    situation_compromising.print_preference_matrix()
    run_voting_schemes(situation_compromising, "Compromising")

    # Burying Strategy:
    situation_burying.strategies.burying()
    print("\n=== After Strategic (Burying) Adjustment ===")
    situation_burying.print_preference_matrix()
    run_voting_schemes(situation_burying, "Burying")


if __name__ == "__main__":
    main()
