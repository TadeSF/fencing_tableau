import itertools
import os
import platform
import random
import time

import csv_util
from fencer import *
from match import *
from deprecated.elimination_tree import *
from deprecated.standing import *
from deprecated.prelim_groups import PreliminaryGroup



# ----- Global variables -----
fencing_pistes = 0          # Number of pistes
preliminary_groups = 0      # Number of groups in the preliminary round
piste_counter = 1           # Counter for piste assignment



# ----- MISC -----
def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")



# ----- Run on startup -----
clear_console()

# ask if user wants to simulate results
if input("Do you want to simulate the results? (y/n) ").lower() == "y":
    simulate_results = True
    # ask how high the win score should be  
    simulation_win_points = int(input("How many points should the winner have? "))
else:
    simulate_results = False
clear_console()



# ----- Functions -----


def enter_prelim_live(matches: list, groups: list, fencers: list) -> Standings:
    # Wait for user to press enter
    input("Press enter to continue into live mode...")

    # Clear the console
    clear_console()

    print("Live Mode")
    print("---------\n")
    print("The program will wait for you to input the results of the matches.\n\n")

    # Loop through each round
    for round in matches:
        # While the round is not completed
        while True:
            # Print matches of the round
            print("Round " + str(matches.index(round) + 1))
            print("-------")
            print("")
            for match in round:
                print(match)
                print("")
            
            # Show fencers of the next round to get ready
            if matches.index(round) + 1 < len(matches):
                print("Fencers of the next round:")
                print_string = ""
                for match in matches[matches.index(round) + 1]:
                    print_string += f"   {match.green.short_str()} vs. {match.red.short_str()}\n"
                print(print_string[:-1])
                print("")
            print("-------\n")

            try:
                # If all matches have been completed, break out of the loop
                if all([match.match_completed for match in round]):
                    break

                # Ask user for match ID
                # If simulation is enabled, pick a random match
                if simulate_results:
                    match_id = random.choice([match.id for match in round if not match.match_completed])
                else:
                    match_id = int(input("Please enter the ID of the match you want to input the results for: "))
                    print("")

                # Check if match ID is valid
                if match_id not in [match.id for match in round]:
                    raise ValueError("Invalid match ID\n")

                # Search for match
                for match in round:
                    if match.id == match_id:
                        # Ask user for match results
                        # if simulation is enabled, pick random scores
                        if simulate_results:
                            # randomly pick a winner
                            winner = random.choice([match.green, match.red])
                            # randomly pick a score against the winner
                            loser_score = random.randint(0, simulation_win_points - 1)
                            green_score = 5 if winner == match.green else loser_score
                            red_score = 5 if winner == match.red else loser_score
                        else:
                            green_score = int(input(f"Please enter the score for the green fencer {match.green.short_str()}: "))
                            red_score = int(input(f"Please enter the score for the red fencer {match.red.short_str()}: "))
                            print("")

                        # Save results
                        match.input_results(green_score, red_score)

                        # Print the results
                        print(match.score)
                        print("")

                        # Clear the console
                        clear_console()

                        break

            # Catch input errors
            except ValueError as e:
                print(e)
                continue

        
        # End Round
        print("Done with round " + str(matches.index(round) + 1))
        print("")
        print("-----------------------------------------")
        print("")

    print("Done with all rounds")
    print("")

    # Clear the console after hitting enter
    print("\n\n")
    input("Press enter to continue...")
    clear_console()

    # Show final results
    print("Final Results of Groups")
    print("-------------")
    print("")
    for group in groups:
        print("Group " + group.group_letter)
        print("-------")
        print("")
        for match in group.matches:
            print(match)
            print("")
            time.sleep(0.01)
        print("\n")

    # Clear the console on enter
    print("\n\n")
    input("Press enter to continue...")
    print("\n\n")
    clear_console()
    print("\n\n")

    # Show Standings
    current_standings = Standings(fencers, copy_fencers=False)

    print(current_standings.print_standings("preliminary", groups=True))
    print(current_standings.print_standings("preliminary", groups=False))

    # wait for enter
    print("\n\n")
    input("Press enter to continue...")

    return current_standings


def enter_intermediate_live(matches: list, groups: list):
    pass
    # TODO – implement intermediate live mode





def piste_assignmet() -> int:
    global piste_counter, fencing_pistes

    if fencing_pistes == 1:
        # Only one piste
        return 1
    else:
        # Assign piste if more than two pistes
        piste = piste_counter
        if piste_counter == fencing_pistes:
            # Reset piste counter if it reaches the maximum number of pistes
            piste_counter = 1
        else:
            # Increment piste counter for next match
            piste_counter += 1
        
        return piste


def assign_fencers() -> list:
    # ask for CSV file or manual input
    if input("\nDo you want to import a CSV file? (y/n): ").lower() == "y":
        csv_file = input("Please enter the full path to the CSV file: \n")
        fencers = csv_util.read_fencer_csv_file(csv_file)
    else:
        fencers = []
        print("Please enter the fencers manually (press enter to stop): ")
        while True:
            fencer_name = input("Please enter the name of the fencer: ")
            if fencer_name == "":
                break
            fencer_club = input("Please enter the club of the fencer: ")
            fencer_nationality = input("Please enter the nationality of the fencer: ")
            print("------")
            fencers.append(Fencer(fencer_name, fencer_club if fencer_club != "" else None, fencer_nationality if fencer_nationality != "" else None))

    # Assign start numbers
    for i in range(len(fencers)):
        fencers[i].start_number = i + 1

    # Print all participanting fencers
    print("")
    print("The following fencers are participating:")
    print("Start Number | Name (Nationality) | Club")
    print("")
    for fencer in fencers:
        print(fencer)
        time.sleep(0.01)

    print("")
    print("------------------------------------")
    print("")

    # Return the fencers
    return fencers



def create_prelimenary_tableau():
    global fencing_pistes, preliminary_groups

    # Assign fencers to the tableau
    fencers = assign_fencers()


    # Ask for turnament configuration
    print("")
    print("Please enter the turnament configuration: ")
    # Number of fencing pistes
    fencing_pistes = int(input("How many fencing pistes are there? (1-12): "))
    if fencing_pistes < 1 or fencing_pistes > 12:
        raise ValueError("Number of fencing pistes must be between 1 and 4")

    # Ask if the number of preliminary groups should be calculated automatically
    if input("Do you want to calculate the number of preliminary groups automatically? (y/n): ").lower() == "y":
        # Calculate the number of preliminary groups
        # All Groups should have the same number of fencers
        # In the best case, there should be between 5 and 8 fencers per group.
        # The number of groups should be as low as possible
        preliminary_groups = len(fencers) // 6
        if preliminary_groups % 6 > 0:
            preliminary_groups += 1

        # Calculate the number of groups
        preliminary_groups = len(fencers) // 5

    else:
        preliminary_groups = int(input("How many preliminary groups are there? (1-16): "))

    # Randomize fencers before grouping
    random.shuffle(fencers)

    # Split fencers into groups
    for fencer in fencers:
        fencer.prelim_group = fencers.index(fencer) % preliminary_groups + 1

    # Create group objects with the according fencers
    groups = []
    for i in range(preliminary_groups):
        groups.append(PreliminaryGroup([fencer for fencer in fencers if fencer.prelim_group == i + 1], i + 1))

    # Print Grouping
    print("")
    print("The fencers have been grouped as follows: ")
    print("")
    for group in groups:
        print("Group " + group.group_letter)
        print("-------")
        for fencer in group.fencers:
            print(fencer)
            time.sleep(0.01)
        print("")
    print("")

    time.sleep(1)


    preliminary_matches = []

    combinations = [] # List of all possible combinations of fencers

    # Get all possible combinations of matches
    for group in groups:
        combinations.extend(group.combinations)

    used_fencers = [] # List of fencers that have already been used in a match, used to prevent fencers from fighting multiple times at the same time

    timeout_counter = 0 # Counter to prevent infinite loop if there are not enough fencers to fill all pistes
    double_warning = False # Boolean to enable a warning from being printed if there are not enough fencers to fill all pistes

    # TODO – Implement the following rules of the Deutscher Fechter-Bund for the preliminary tableau:
    ''' Eine aktuelle Landesrangliste oder deutsche Rangliste hilft uns,
    die Turnierfavoriten gleichmäßig auf die Gruppen zu verteilen.
    Außerdem sollte nie mehr als ein Fechter vom selben Verein
    (bei internationalen Turnieren aus demselben Land) in einer Gruppe sein.
    Das geht natürlich nicht immer. Wenn wir zehn Gruppen haben,
    aber einen Verein mit zwölf Teilnehmern, dann wird es eben zwei Gruppen geben,
    wo je zwei Vereinskollegen zusammen fechten.
    Die müssen dann aber das allererste Gefecht gegeneinander machen.'''


    # Create the matches
    while len(combinations) > 0:
        for fencer_1, fencer_2 in combinations:
            # Check if the fencers have already been used
            if fencer_1 not in used_fencers and fencer_2 not in used_fencers:

                # Check if the fencers are in the same group
                if fencer_1.prelim_group == fencer_2.prelim_group:
                    for group in groups:
                        if group.group_number == fencer_1.prelim_group:
                            # Create the match
                            preliminary_matches.append(Match(fencer_1, fencer_2, group))
                            # Add the match to the group
                            group.matches.append(preliminary_matches[-1])
                            break
                else:
                    raise ValueError("Fencers are not in the same group")

                # Add the fencers to the list of used fencers
                used_fencers.append(fencer_1)
                used_fencers.append(fencer_2)

                # Remove the combination from the list of combinations
                combinations.remove((fencer_1, fencer_2))

                # Reset the timeout counter
                timeout_counter = 0
            
                # Check if all pistes are filled and reset the list of used fencers
                if len(used_fencers) == fencing_pistes * 2:
                    used_fencers = []
            
        # Timeout to prevent infinite loop if there are not enough fencers to fill all pistes
        if timeout_counter > 100:
            used_fencers = []
            timeout_counter = 0
            double_warning = True # Enable warning
        else:
            timeout_counter += 1

    
    # Group the matches into groups of number of pistes
    preliminary_matches = [preliminary_matches[i:i + fencing_pistes] for i in range(0, len(preliminary_matches), fencing_pistes)]

    # Assign pistes to the matches
    for i in range(len(preliminary_matches)):
        for j in range(len(preliminary_matches[i])):
            preliminary_matches[i][j].piste = piste_assignmet()

    
 

    # Print the preliminary matches
    print("")
    print("The following matches are in the preliminary round:")

    if double_warning is True:
        print("WARNING: At least one fencer will be fighting on at least two pistes at the same time!")

    print("Match Number | Green Fencer | Red Fencer | Piste")
    print("")

    for group in preliminary_matches:
        print(" ")
        for match in group:
            print(match)
            time.sleep(0.01)
        time.sleep(0.05)

    return preliminary_matches, groups, fencers



def create_intermediate_tableau(fencers: list):
    pass
    # TODO – Implement intermediate tableau






# ----- Run the program -----

if __name__ == "__main__": # Only run the program if it is run directly, not if it is imported

    #clear the console
    clear_console()
    
    # Welcome message
    print("Welcome to the Fencing Tableau Generator!\n----------------------------------------\n")
    print("This program will generate a tableau for you to use in your fencing competitions.\n")
    print("The program will generate a tableau for a preliminary round, a direct elimination round, and finals.")
    print("The program will also generate a statistics sheet for you to use to keep track of your fencers' statistics.")
    print("You can also import a CSV file with your fencers' information to save time. Just make sure the CSV file is formatted correctly: \n Name, Club, Nationality\n")


    # --- Preliminary Round ---

    # Create the prelimenary tableau
    list_of_preliminary_matches, list_of_preliminary_groups, list_of_all_fencers = create_prelimenary_tableau()

    # Ask if the user wants to run the program in live mode or generate a csv file for the preliminary round
    # Live Mode – The program will wait for the user to input all results of a round and to continue to the next round
    # CSV Mode – The program will generate a CSV file with all the matches and the user will have to input the results in a spreadsheet program. Afterwards the CSV can be imported into the program to continue the turnament
    live_mode = input("Do you want to run the program in live mode or generate a csv? (live/csv): ")


    # CSV Mode
    if live_mode == "csv":
        csv_util.export_preliminary_matches(list_of_preliminary_matches, list_of_preliminary_groups)
        #TODO – Add mechanism to continue the turnament after the CSV file has been imported

    # Live Mode
    else:
        prelim_standings = enter_prelim_live(list_of_preliminary_matches, list_of_preliminary_groups, list_of_all_fencers)



    # --- Intermediate Round ---

    # Only a third of all fencers can be eliminated in the preliminary round, so there will be an intermediate round
    #TODO – Add intermediate round

    # First, calculate if a intermediate round is needed
    # If a round of "only" 32 fencers doesn't eliminate a third of all fencers, then the intermediate round will be skipped
    if len(list_of_all_fencers) <= 32 or len(list_of_all_fencers) - 32 < len(list_of_all_fencers) / 3:
        intermediate_round_needed = False

    # If the intermediate round is needed, create the intermediate tableau
    else:
        intermediate_round_needed = True
        # Create the intermediate tableau
        list_of_intermediate_matches, list_of_intermediate_groups, list_of_intermediate_fencers = create_intermediate_tableau(list_of_all_fencers)


        # CSV Mode
        if live_mode == "csv":
            csv_util.export_intermediate_matches(list_of_intermediate_matches, list_of_intermediate_groups)
            #TODO – Add mechanism to continue the turnament after the CSV file has been imported

        # Live Mode
        elif live_mode == "live":
            enter_intermediate_live(list_of_intermediate_matches, list_of_intermediate_groups)



    # --- Direct Elimination Round ---

    # The direct elimination round is the final of the turnament and is held by a maximum of 32 fencers

    # Create the direct elimination tree
    Tree = EliminationTree(list_of_all_fencers)

    print("Direct Elimination Round")
    print("------------------------")

    while Tree.round_counter != 1:
        # Create Matches
        Tree.create_matches()


        # Group the matches into groups of number of pistes
        Tree.matches[Tree.round_counter] = [Tree.matches[Tree.round_counter][i:i + fencing_pistes] for i in range(0, len(Tree.matches[Tree.round_counter]), fencing_pistes)]

        # Assign pistes to the matches
        piste_counter = 1
        for i in range(len(Tree.matches[Tree.round_counter])):
            for j in range(len(Tree.matches[Tree.round_counter][i])):
                if Tree.matches[Tree.round_counter][i][j].wildcard == False:
                    Tree.matches[Tree.round_counter][i][j].piste = piste_assignmet()
                else:
                    Tree.matches[Tree.round_counter][i][j].piste = 0

        # Print the matches
        for match in Tree.matches:
            print(match)

        # Clear the console
        clear_console()



        # Loop through each round
        for round in Tree.matches[Tree.round_counter]:
            # While the round is not completed
            while True:
                print("Direct Elimination Round")
                print("------------------------\n")

                print(f"Currently: {Tree.round()}\n\n")


                # Print matches of the round
                print("Round " + str(Tree.matches[Tree.round_counter].index(round) + 1))
                print("-------")
                print("")
                for match in round:
                    print(match)
                    print("")
                
                # Show fencers of the next round to get ready
                if Tree.matches[Tree.round_counter].index(round) + 1 < len(Tree.matches[Tree.round_counter]):
                    print("Fencers of the next round:")
                    print_string = ""
                    for match in Tree.matches[Tree.round_counter][Tree.matches[Tree.round_counter].index(round) + 1]:
                        print_string += f"   {match.green.short_str()} vs. {match.red.short_str()}\n"
                    print(print_string[:-1])
                    print("")
                print("-------\n")

                try:
                    # If all matches have been completed, break out of the loop
                    if all([match.match_completed for match in round]):
                        break

                    # Ask user for match ID
                    # If simulation is enabled, pick a random match
                    if simulate_results:
                        match_id = random.choice([match.id for match in round if not match.match_completed])
                    else:
                        match_id = int(input("Please enter the ID of the match you want to input the results for: "))
                        print("")

                    # Check if match ID is valid
                    if match_id not in [match.id for match in round]:
                        raise ValueError("Invalid match ID\n")

                    # Search for match
                    for match in round:
                        if match.id == match_id:
                            # Ask user for match results
                            # if simulation is enabled, pick random scores
                            if simulate_results:
                                # randomly pick a winner
                                winner = random.choice([match.green, match.red])
                                # randomly pick a score against the winner
                                loser_score = random.randint(0, simulation_win_points - 1)
                                green_score = simulation_win_points if winner == match.green else loser_score
                                red_score = simulation_win_points if winner == match.red else loser_score
                            else:
                                green_score = int(input(f"Please enter the score for the green fencer {match.green.short_str()}: "))
                                red_score = int(input(f"Please enter the score for the red fencer {match.red.short_str()}: "))
                                print("")

                            # Save results
                            match.input_results(green_score, red_score)

                            # Print the results
                            print(match.score)
                            print("")

                            # wait for enter
                            input("Press enter to continue...")

                            # Clear the console
                            clear_console()

                            break
                
                # Catch input errors
                except ValueError as e:
                    print(e)
                    continue

            
            # End Round
            print("Done with round " + str(Tree.matches[Tree.round_counter].index(round) + 1))

            # wait for enter
            input("Press enter to continue...")

            # Clear the console
            clear_console()

        # Done with round
        print("Done with round " + Tree.round())
        print("")
        Tree.round_counter -= 1

        # wait for enter
        input("Press enter to continue...")

    # Final and Bronze Medal Match

    # Create Matches
    Tree.create_matches()

    while True:

        # Print the matches
        print("Final")
        print("-----\n")
        print("")
        print(Tree.matches[1][0])
        print("\n\n")
        print("Bronze Medal Match")
        print("------------------")
        print("")
        print(Tree.matches[0][0])
        print("\n\n")

        try:
            # If all matches have been completed, break out of the loop
            if Tree.matches[1][0].match_completed and Tree.matches[1][0].match_completed:
                break

            round = [Tree.matches[1][0], Tree.matches[0][0]]

            # Ask user for match ID
            # If simulation is enabled, pick a random match
            if simulate_results:
                match_id = random.choice([match.id for match in round if not match.match_completed])
            else:
                match_id = int(input("Please enter the ID of the match you want to input the results for: "))
                print("")

            # Check if match ID is valid
            if match_id not in [match.id for match in round]:
                raise ValueError("Invalid match ID\n")

            # Search for match
            for match in round:
                if match.id == match_id:
                    # Ask user for match results
                    # if simulation is enabled, pick random scores
                    if simulate_results:
                        # randomly pick a winner
                        winner = random.choice([match.green, match.red])
                        # randomly pick a score against the winner
                        loser_score = random.randint(0, simulation_win_points - 1)
                        green_score = simulation_win_points if winner == match.green else loser_score
                        red_score = simulation_win_points if winner == match.red else loser_score
                    else:
                        green_score = int(input(f"Please enter the score for the green fencer {match.green.short_str()}: "))
                        red_score = int(input(f"Please enter the score for the red fencer {match.red.short_str()}: "))
                        print("")

                    # Save results
                    match.input_results(green_score, red_score)

                    # Print the results
                    print(match.score)
                    print("")

                    # wait for enter
                    input("Press enter to continue...")

                    # Clear the console
                    clear_console()

                    break
        
        # Catch input errors
        except ValueError as e:
            print(e)
            continue

    # clear the console
    clear_console()

    # Print the results
    final_standings = Standings(list_of_all_fencers)
    print(final_standings.print_standings("combined"))





    

