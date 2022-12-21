

import json


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







def assign_fencers():
    pass

def create_tableau():
    # Players
    # fencers = assign_fencers()
    pass


# Run the program
if __name__ == "__main__":
    create_tableau()

    fencer = Fencer("John", nationailty="Germany")
    print(fencer)