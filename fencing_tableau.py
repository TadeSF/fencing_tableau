import itertools
import json
import random
import time


# Global variables
fencing_pistes = 0
preliminary_rounds = 0

piste_counter = 1


# Main Class for every individual fencer
class Fencer:

    def __init__(self, name: str, club: str = None, nationailty: str = None):
        # Start number
        self.start_number = None

        # Fencer information
        self.name = name
        self.club = club

        if nationailty is not None:
            # Get 3 character nationality code if not already
            if len(nationailty) != 3:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                    for country in countries:
                        if nationailty == country["name"]:
                            nationailty = country["alpha-3"]
                            break
                    else:
                        raise ValueError("No valid (english) country input / Nationailty must be 3 characters long")

        self.nationality = nationailty

        # Statistics
        self.wins = 0
        self.losses = 0
        self.points_for = 0
        self.points_against = 0


    def __str__(self) -> str:
        if self.club is None and self.nationality:
            string_to_return = f"{self.start_number} {self.name} ({self.nationality})"
        elif self.club and self.nationality is None:
            string_to_return = f"{self.start_number} {self.name} / {self.club}"
        elif self.club and self.nationality:
            string_to_return = f"{self.start_number} {self.name} ({self.nationality}) / {self.club}"
        else:
            string_to_return = f"{self.start_number} {self.name}"
        return string_to_return

    def short_str(self) -> str:
        return f"{self.start_number} {self.name}"


    # statistics
    def update_statistics(self, win: bool, points_for: int, points_against: int):
        if win:
            self.wins += 1
        else:
            self.losses += 1

        self.points_for += points_for
        self.points_against += points_against

    @property
    def win_percentage(self) -> float:
        return self.wins / (self.wins + self.losses)
    
    @property
    def points_difference(self) -> int:
        return self.points_for - self.points_against

    @property
    def points_per_game(self) -> float:
        return self.points_for / (self.wins + self.losses)

    @property
    def points_against_per_game(self) -> float:
        return self.points_against / (self.wins + self.losses)


class Match:
    id = 1
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int = None, elimination: bool = False):
        # ID
        self.id = Match.id
        Match.id += 1

        # Match information
        self.match_number = None
        self.elimination = elimination
        self.piste = fencing_piste
        self.match_completed = False

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Score
        self.green_score = 0
        self.red_score = 0

    
    def __str__(self) -> str:
        if self.match_completed:
            return_str = self.score
        else:
            return_str = f"Match {self.id}:   {self.green.short_str()} vs. {self.red.short_str()}   (Piste {self.piste})"
        return return_str


    # Statistics
    @property
    def score(self) -> str:
        return f"Match {self.id} Result:   {self.green.short_str().upper() if self.green == self.winner else self.green.short_str()}   {self.green_score}:{self.red_score}   {self.red.short_str().upper() if self.red == self.winner else self.red.short_str()}   (Piste {self.piste})"

    @property
    def winner(self) -> Fencer:
        if self.green_score > self.red_score:
            return self.green
        elif self.red_score > self.green_score:
            return self.red
        else:
            return None
    
    @property
    def loser(self) -> Fencer:
        if self.green_score < self.red_score:
            return self.red
        elif self.red_score > self.green_score:
            return self.green
        else:
            return None

    # Input Results
    def input_results(self, green_score: int, red_score: int):
        # Check for invalid score
        if green_score < 0 or red_score < 0:
            raise ValueError("Score must be a positive integer")
        elif green_score == red_score:
            raise ValueError("Score must be different")

        # Valid score
        else:
            self.green_score = green_score
            self.red_score = red_score
            self.match_completed = True
        
            # Update statistics
            self.green.update_statistics(True if self.winner == self.green else False, self.green_score, self.red_score)
            self.red.update_statistics(False if self.winner == self.green else True, self.red_score, self.green_score)








# MISC Functions
def read_fencer_csv_file(file_path: str) -> list:
    with open(file_path, "r") as f:
        csv_file = f.readlines()

    # Remove the first line (headers) if it exists
    if csv_file[0].startswith("Name"):
        csv_file.pop(0)
    
    # Create a dictionary of fencers
    fencers = []
    for line in csv_file:
        line = line.split(",")
        fencer_name = line[0].strip()
        fencer_club = line[1].strip()
        fencer_nationality = line[2].strip()
        fencers.append(Fencer(fencer_name, fencer_club if fencer_club != "" else None, fencer_nationality if fencer_nationality != "" else None))
    
    return fencers


def export_preliminary_matches(matches: list, file_path: str = None):
    if file_path is None:
        file_path = input("Please enter the full path to the file you want to export to: \n")

    with open(file_path, "w") as f:
        for match in matches:
            # TODO – Continue here
            f.write(f"{match.green.name},{match.red.name},{match.piste}\n")


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
    print("\n" * 100)

    print("Live Mode")
    print("---------\n")
    print("The program will wait for you to input the results of the matches.\n\n")

    # Loop through each round
    for round in matches:
        # While the round is not completed
        while True:
            # Print matches of the round
            print("Round " + str(matches.index(round) + 1))
            time.sleep(0.5)
            print("-------")
            print("")
            for match in round:
                print(match)
                print("")
                time.sleep(0.1)
            
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
                match_id = int(input("Please enter the ID of the match you want to input the results for: "))
                print("")

                # Check if match ID is valid
                if match_id not in [match.id for match in round]:
                    raise ValueError("Invalid match ID\n")

                # Search for match
                for match in round:
                    if match.id == match_id:
                        # Ask user for match results
                        green_score = int(input(f"Please enter the score for the green fencer {match.green.short_str()}: "))
                        red_score = int(input(f"Please enter the score for the red fencer {match.red.short_str()}: "))
                        print("")

                        # Save results
                        match.input_results(green_score, red_score)

                        # Print the results
                        print(match.score)
                        print("")

                        time.sleep(1)

                        # Clear the console
                        print("\n" * 100)

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
        time.sleep(0.5)

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
            time.sleep(0.1)
    print("-------------\n")

    # Clear the console on enter
    print("\n\n")
    input("Press enter to continue...")
    print("\n" * 100)

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


    # Shuffle the fencers
    random.shuffle(fencers)

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
        time.sleep(0.1)

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
    # preliminary_rounds = int(input("How many groups in the preliminary round are there? (1-4): "))
    # if preliminary_rounds < 1 or preliminary_rounds > 4:
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
            time.sleep(0.1)
        time.sleep(0.2)

    return preliminary_matches


# ------------------------------------ #

# Run the program
if __name__ == "__main__":
    #clear the console
    print("\n" * 100)
    
    # Welcome message
    print("Welcome to the Fencing Tableau Generator!\n----------------------------------------\n")
    print("This program will generate a tableau for you to use in your fencing competitions.\n")
    print("The program will generate a tableau for a preliminary round, a direct elimination round, and finals.\n")
    print("The program will also generate a statistics sheet for you to use to keep track of your fencers' statistics.\n")
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

    

