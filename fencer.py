import json
from typing import Literal

from enum import Enum

# Enum for the different advancement stages of a fencer
class Stage(Enum):
    PRELIMINARY = 7
    INTERMEDIATE = 6
    TOP_32 = 5
    TOP_16 = 4
    QUARTER_FINALS = 3
    SEMI_FINALS = 2
    THIRD_PLACE_FINAL = -1
    GRAND_FINAL = 1



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

        # Past opponents (for repechage)
        self.group_opponents = [] # This is needed for matchmaking in the direct elimination stage when repechage is used.

        # Stage information
        self.stage: Stage = Stage.PRELIMINARY # Tracks the advancement of the fencer (to determine standings)
        

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
    def update_statistics(self, win: bool, opponent, points_for: int, points_against: int):
        if self.stage == Stage.PRELIMINARY or self.stage == Stage.INTERMEDIATE:
            stage = self.stage.name.lower()
        else:
            stage = "elimination"

        if win:
            self.statistics["overall"]["wins"] += 1
            self.statistics[stage]["wins"] += 1
        else:
            self.statistics["overall"]["losses"] += 1
            self.statistics[stage]["losses"] += 1

        self.statistics["overall"]["matches"] += 1
        self.statistics["overall"]["points_for"] += points_for
        self.statistics["overall"]["points_against"] += points_against

        self.statistics[stage]["matches"] += 1
        self.statistics[stage]["points_for"] += points_for
        self.statistics[stage]["points_against"] += points_against

        self.group_opponents.append(opponent)


    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return (round(self.statistics[stage]["wins"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> str:
        difference = self.statistics[stage]["points_for"] - self.statistics[stage]["points_against"]
        return str("+" + str(difference) if difference > 0 else str(difference))

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return (round(self.statistics[stage]["points_for"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return (round(self.statistics[stage]["points_against"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)




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