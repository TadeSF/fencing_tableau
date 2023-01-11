"""
fencer.py

This module contains the Fencer class. Every participant in a Tournament gets a Fencer object.
This module also holds the different Stage enums of the Tournament.
"""

import json
from typing import Literal

from enum import Enum

# Enum for the different advancement stages of a fencer
class Stage(Enum):
    PRELIMINARY_ROUND = -1
    PLACEMENTS = -2

    TOP_1024 = 10
    TOP_512 = 9
    TOP_256 = 8
    TOP_128 = 7
    TOP_64 = 6
    TOP_32 = 5
    TOP_16 = 4
    QUARTER_FINALS = 3
    SEMI_FINALS = 2
    GRAND_FINAL = 1
    FINISHED = 0

    def __str__(self):
        return self.name.replace("_", " ").title()

    def next_stage(self):
        if self.value != 1:
            return Stage(self.value - 1)



# Main Class for every individual fencer
class Fencer:
    """
    Fencer class
    """

    def __init__(self, name: str, club: str = None, nationailty: str = None, start_number: int = None, num_prelim_rounds: int = 1):
        """
        Constructor for the Fencer class

        :param name: Name of the fencer
        :param club: Club of the fencer
        :param nationailty: Nationailty of the fencer
        :param start_number: Start number of the fencer
        :param num_prelim_rounds: Number of preliminary rounds

        :type name: str
        :type club: str
        :type nationailty: str
        :type start_number: int
        :type num_prelim_rounds: int
        
        :raises ValueError: If the nationailty is not a 3 character code
        """
        # Start number
        self.start_number = start_number

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

        # Elimination Value
        self.elimination_value = None # This Index is used for calculating the next opponent in the elimination stage
        self.last_match_won = False

        # Past opponents (for repechage)
        self.group_opponents = [] # This is needed for matchmaking in the direct elimination stage when repechage is used.

        # Stage information
        self.stage: Stage = Stage.PRELIMINARY_ROUND # Tracks the advancement of the fencer (to determine standings)
        self.eliminated = False # Tracks if the fencer has been eliminated from the tournament

        # Final Rank
        self.final_rank = None



        # Statistics
        self.statistics = {
            "overall": {
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            },
            "preliminary_round": [],
            "elimination": [
                {
                    "matches": 0,
                    "wins": 0,
                    "losses": 0,
                    "points_for": 0,
                    "points_against": 0
                }
            ]
        }

        for _ in range(num_prelim_rounds):
            self.statistics["preliminary_round"].append({
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            })



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

    @property
    def short_str(self) -> str:
        return f"{self.start_number}   {self.name}"


    # statistics
    def update_statistics(self, win: bool, opponent, points_for: int, points_against: int, round: int = 0):
        if self.stage == Stage.PRELIMINARY_ROUND:
            stage = self.stage.name.lower()
        else:
            stage = "elimination"

        if win:
            self.statistics["overall"]["wins"] += 1
            self.statistics[stage][round]["wins"] += 1
            self.last_match_won = True
        else:
            self.statistics["overall"]["losses"] += 1
            self.statistics[stage][round]["losses"] += 1
            self.last_match_won = False

        self.statistics["overall"]["matches"] += 1
        self.statistics["overall"]["points_for"] += points_for
        self.statistics["overall"]["points_against"] += points_against

        self.statistics[stage][round]["matches"] += 1
        self.statistics[stage][round]["points_for"] += points_for
        self.statistics[stage][round]["points_against"] += points_against

        self.group_opponents.append(opponent)


    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> int:
        return int(round((self.statistics[stage]["wins"]*1.0) / (self.statistics[stage]["matches"]*1.0)*100) if self.statistics[stage]["matches"] != 0 else 0)

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> str:
        difference = self.statistics[stage]["points_for"] - self.statistics[stage]["points_against"]
        return str("+" + str(difference) if difference > 0 else str(difference))
    
    def points_difference_int(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> int:
        difference = self.statistics[stage]["points_for"] - self.statistics[stage]["points_against"]
        return int(difference)

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return (round(self.statistics[stage]["points_for"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        return (round(self.statistics[stage]["points_against"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)




class Wildcard(Fencer):
    def __init__(self, wildcard_number: int):
        super().__init__("Wildcard", nationailty="WLD")
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

    def update_statistics(self, win: bool, opponent, points_for: int, points_against: int, round: int = 0):
        raise(TypeError("Wildcard has no statistics like a normal fencer"))