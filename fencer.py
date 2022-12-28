import json
from typing import Literal


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

        # Grouping information
        self.prelim_group = None
        self.intermediate_group = None

        # Stage information
        self.stage: Literal["preliminary", "intermediate", "elimination"] = "preliminary"
        
        # Final Placement information
        self.podium = None # This is needed for calculating the final ranking. First place = 1, second place = 2, third place = 3, fourth pace = 4, rest = None

        # Statistics
        self.statistics = {
            "overall": {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            },
            "preliminary": {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            },
            "intermediate": {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            },
            "elimination": {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            }
        }

        self.rank = {
            "preliminary": None,
            "intermediate": None,
            "elimination": None,
            "overall": None,
            "combined": None
        }


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
            self.statistics["overall"]["wins"] += 1
            self.statistics[self.stage]["wins"] += 1
        else:
            self.statistics["overall"]["losses"] += 1
            self.statistics[self.stage]["losses"] += 1

        self.statistics["overall"]["matches"] += 1
        self.statistics["overall"]["points_for"] += points_for
        self.statistics["overall"]["points_against"] += points_against

        self.statistics[self.stage]["matches"] += 1
        self.statistics[self.stage]["points_for"] += points_for
        self.statistics[self.stage]["points_against"] += points_against


    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return round(self.statistics[stage]["wins"] / self.statistics[stage]["matches"], 2)

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> str:
        difference = self.statistics[stage]["points_for"] - self.statistics[stage]["points_against"]
        return str("+" + str(difference) if difference > 0 else str(difference))

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return round(self.statistics[stage]["points_for"] / self.statistics[stage]["matches"], 2)

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return round(self.statistics[stage]["points_against"] / self.statistics[stage]["matches"], 2)




class Wildcard(Fencer):
    def __init__(self, wildcard_number: int):
        super().__init__("Wildcard")
        self.wildcard_number = wildcard_number
        self.start_number = 0

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def update_statistics(self, win: bool, points_for: int, points_against: int):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))