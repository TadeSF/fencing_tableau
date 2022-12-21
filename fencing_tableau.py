

import json


# Main Class for every individual fencer
class Fencer:
    def __init__(self, name: str, club: str = None, nationailty: str = None):
        self.name = name
        self.club = club

        # Get 3 character nationality code if not already
        if nationailty is not None:
            if len(nationailty) != 3:
                with open("countries.json", "r") as f:
                    print("Loading countries...")
                    countries = json.load(f)
                    for country in countries:
                        if nationailty == country["name"]:
                            nationailty = country["alpha-3"]
                            break
                    else:
                        raise ValueError("Nationailty must be 3 characters long")

        self.nationality = nationailty

        # Statistics
        self.wins = 0
        self.losses = 0
        self.points_for = 0
        self.points_against = 0

    def __str__(self) -> str:
        if self.club is None and self.nationality:
            string_to_return = f"{self.name} ({self.nationality})"
        elif self.club and self.nationality is None:
            string_to_return = f"{self.name} / {self.club}"
        elif self.club and self.nationality:
            string_to_return = f"{self.name} ({self.nationality}) / {self.club}"
        return string_to_return

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



# MISC FUNCTIONS
def read_fencer_csv_file(file_path: str) -> dict:
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
        fencers.append(Fencer(fencer_name, fencer_club, fencer_nationality))


def assign_fencers() -> list:
    # ask for CSV file or manual input
    if input("Do you want to import a CSV file? (y/n): ").lower() == "y":
        csv_file = input("Please enter the full path to the CSV file: \n")
        fencers = read_fencer_csv_file(csv_file)
    else:
        fencers = []

    return fencers



def create_tableau():
    # Players
    fencers = assign_fencers()

    for fencer in fencers:
        print(fencer)
    
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
    
    # Create the tableau
    create_tableau()

    # Wait for user to press enter
    input("Press enter to continue...", end="\r")

    # Clear the console
    print("\n" * 100)

    # Preliminary Round

    while True:
        #Print next matches
        break


