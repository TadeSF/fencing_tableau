import json


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

        self.prelim_group = None

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
        return round(self.wins / (self.wins + self.losses), 2)
    
    @property
    def points_difference(self) -> str:
        difference = self.points_for - self.points_against
        return str("+" + str(difference) if difference > 0 else str(difference))

    @property
    def points_per_game(self) -> float:
        return round(self.points_for / (self.wins + self.losses), 2)

    @property
    def points_against_per_game(self) -> float:
        return round(self.points_against / (self.wins + self.losses), 2)


class Wildcard(Fencer):
    def __init__(self, wildcard_number: int):
        super().__init__("Wildcard")
        self.wildcard_number = wildcard_number
        self.start_number = 0