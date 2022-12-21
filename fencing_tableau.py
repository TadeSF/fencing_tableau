import json
import random
import time


# Global variables
fencing_pistes = 0
preliminary_rounds = 0

points_for_win_in_preliminary_round = 5
points_for_win_in_direct_elimination_round = 10


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
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int, elimination: bool = False):
        # ID
        self.id = Match.id
        Match.id += 1

        # Match information
        self.elimination = elimination
        if self.piste > fencing_pistes or self.piste < 1:
            raise ValueError("Piste number must be between 1 and the number of fencing pistes")
        else:
            self.piste = fencing_piste

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Score
        self.green_score = 0
        self.red_score = 0

    
    def __str__(self) -> str:
        return f"Match {self.id}: {self.green.short_str} vs. {self.red.short_str} on piste {self.piste}"


    # Statistics
    @property
    def winner(self) -> Fencer:
        if self.green_score == (points_for_win_in_direct_elimination_round if self.elimination else points_for_win_in_preliminary_round):
            return self.green
        elif self.red_score == (points_for_win_in_direct_elimination_round if self.elimination else points_for_win_in_preliminary_round):
            return self.red
        else:
            return None
    
    @property
    def loser(self) -> Fencer:
        if self.green_score == (points_for_win_in_direct_elimination_round if self.elimination else points_for_win_in_preliminary_round):
            return self.red
        elif self.red_score == (points_for_win_in_direct_elimination_round if self.elimination else points_for_win_in_preliminary_round):
            return self.green
        else:
            return None



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


def assign_fencers() -> list:
    # ask for CSV file or manual input
    if input("Do you want to import a CSV file? (y/n): ").lower() == "y":
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
    # Assign fencers to the tableau
    fencers = assign_fencers()


    # Ask for turnament configuration
    print("")
    print("Please enter the turnament configuration: ")
    # Number of fencing pistes
    fencing_pistes = int(input("How many fencing pistes are there? (1-4): "))
    if fencing_pistes < 1 or fencing_pistes > 4:
        raise ValueError("Number of fencing pistes must be between 1 and 4")

    # Number of separate groups of preliminary rounds
    preliminary_rounds = int(input("How many groups of preliminary rounds are there? (1-4): "))
    if preliminary_rounds < 1 or preliminary_rounds > 4:
        raise ValueError("Number of preliminary rounds must be between 1 and 4")

    # Number of points for a win in a preliminary round
    points_for_win_in_preliminary_round = int(input("How many points are needed for a win in the preliminary round? (1-15 | standard: 5): "))
    if points_for_win_in_preliminary_round < 1 or points_for_win_in_preliminary_round > 15:
        raise ValueError("Number of points for a win in a preliminary round must be between 1 and 15")
    
    # Number of points for a win in a direct elimination round
    points_for_win_in_direct_elimination_round = int(input("How many points are needed for a win in the direct elimination round? (1-15 | standard: 10): "))
    if points_for_win_in_direct_elimination_round < 1 or points_for_win_in_direct_elimination_round > 15:
        raise ValueError("Number of points for a win in a direct elimination round must be between 1 and 15")






    



    return None


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
    create_prelimenary_tableau()

    # Wait for user to press enter
    input("Press enter to continue...")

    # Clear the console
    print("\n" * 100)

    # Preliminary Round

    while True:
        #Print next matches
        break


