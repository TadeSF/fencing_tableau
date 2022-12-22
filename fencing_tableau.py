import itertools
import os
import platform
import random
import time

from csv_util import export_preliminary_matches, read_fencer_csv_file
from fencer import Fencer
from match import Match



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
else:
    simulate_results = False
# ask how high the win score should be
simulation_win_points = int(input("How many points should the winner have? "))

clear_console()



# ----- Functions -----

def calculate_standings(matches_group: list) -> list:
    fencers = []
    for matches in matches_group:
        for match in matches:
            if match.green not in fencers:
                fencers.append(match.green)
            if match.red not in fencers:
                fencers.append(match.red)

    # Sort fencers by wins, then points difference, then points for, then points against
    fencers.sort(key=lambda fencer: (fencer.win_percentage, fencer.points_difference, fencer.points_for, fencer.points_against), reverse=True)
    return fencers
    # TODO – Has to be updated once more than one preliminary group is implemented


def enter_live_mode(matches: list):
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

    # Show final results
    print("Done with all rounds")
    print("")

    print("Final Results")
    print("-------------")
    print("")
    for group in matches:
        for match in group:
            print(match)
            print("")
            time.sleep(0.01)
    print("-------------\n")

    # Clear the console on enter
    print("\n\n")
    input("Press enter to continue...")
    clear_console()

    # Show Standings
    print("Standings")
    print("---------")
    print("")
    print("#    Name" + " " * 40 + "W - L   PD   P+ / P-")

    standings = calculate_standings(matches)
    
    for fencer in standings:
        # get index of fencer in the list
        index = standings.index(fencer) + 1
        string_to_print = f"{index}.   {fencer}"

        # Fill the string with spaces to make it look nice
        string_to_print += " " * (50 - len(string_to_print))
        # Add the fencer's stats (wins – losses, points difference, points for / points against)
        string_to_print += f"{fencer.wins} – {fencer.losses}   {fencer.points_difference}   {fencer.points_for} / {fencer.points_against}"

        print(string_to_print)
        print("")





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
        fencers = read_fencer_csv_file(csv_file)
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
    global fencing_pistes

    # Assign fencers to the tableau
    fencers = assign_fencers()


    # Ask for turnament configuration
    print("")
    print("Please enter the turnament configuration: ")
    # Number of fencing pistes
    fencing_pistes = int(input("How many fencing pistes are there? (1-4): "))
    if fencing_pistes < 1 or fencing_pistes > 4:
        raise ValueError("Number of fencing pistes must be between 1 and 4")

    # TODO – Add support for more than 1 group in preliminary round
    # # Number of separate groups of preliminary rounds
    # preliminary_groups = int(input("How many groups in the preliminary round are there? (1-4): "))
    # if preliminary_groups < 1 or preliminary_groups > 4:
    #     raise ValueError("Number of preliminary rounds must be between 1 and 4")

    # create the preliminary matches where every fencer fights every other fencer
    preliminary_matches = []

    # Create all possible combinations of fencers
    combinations = list(itertools.combinations(fencers, 2))

    # Shuffle the combinations
    random.shuffle(combinations)


    used_fencers = [] # List of fencers that have already been used in a match, used to prevent fencers from fighting multiple times at the same time

    timeout_counter = 0 # Counter to prevent infinite loop if there are not enough fencers to fill all pistes
    double_warning = False # Boolean to enable a warning from being printed if there are not enough fencers to fill all pistes

    # Create the matches
    while len(combinations) > 0:
        for fencer_1, fencer_2 in combinations:
            # Check if the fencers have already been used
            if fencer_1 not in used_fencers and fencer_2 not in used_fencers:

                # Create the match
                preliminary_matches.append(Match(fencer_1, fencer_2))

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

    return preliminary_matches





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
    
    # Create the prelimenary tableau
    preliminary_matches = create_prelimenary_tableau()

    # Ask if the user wants to run the program in live mode or generate a csv file for the preliminary round
    # Live Mode – The program will wait for the user to input all results of a round and to continue to the next round
    # CSV Mode – The program will generate a CSV file with all the matches and the user will have to input the results in a spreadsheet program. Afterwards the CSV can be imported into the program to continue the turnament
    live_mode = input("Do you want to run the program in live mode or generate a csv? (live/csv): ")

    #TODO – Add support for more than 1 group in preliminary round

    # CSV Mode
    if live_mode == "csv":
        export_preliminary_matches(preliminary_matches)
        #TODO – Add mechanism to continue the turnament after the CSV file has been imported

    # Live Mode
    elif live_mode == "live":
        enter_live_mode(preliminary_matches)

    

