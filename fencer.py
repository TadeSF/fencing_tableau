import json
import logging
from enum import Enum
from typing import Literal

from attr_checker import check_attr
from random_generator import id

# ------- Logging -------
try: # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('fencer')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    fh = logging.FileHandler('logs/tournament.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
except FileNotFoundError:
    pass

# Enum for the different advancement stages of a fencer
class Stage(Enum):
    """
    Enum for the different advancement stages of a fencer / a match / the tournament in general

    
    ----------------

    - -1 PRELIMINARY_ROUND: 
        The fencer is in the preliminary round
    - -2 PLACEMENTS:
        The fencer has lost in the elimination and is currently in his placement matches

    - 10 TOP_1024:
        The fencer is in the top 1024
    - 9 TOP_512:
        The fencer is in the top 512
    - 8 TOP_256:
        The fencer is in the top 256
    - 7 TOP_128:
        The fencer is in the top 128
    - 6 TOP_64:
        The fencer is in the top 64
    - 5 TOP_32:
        The fencer is in the top 32
    - 4 TOP_16:
        The fencer is in the top 16
    - 3 QUARTER_FINALS:
        The fencer is in the quarter finals
    - 2 SEMI_FINALS:
        The fencer is in the semi finals
    - 1 GRAND_FINAL:
        The fencer is in the grand final

    - 0 FINISHED:
        The fencer has finished the tournament
    """
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
        """
        Returns the name of the stage in a readable format (e.g. "Preliminary Round" instead of "PRELIMINARY_ROUND")
        """
        return self.name.replace("_", " ").title()

    def next_stage(self):
        """
        Advances the stage by one (e.g. TOP_1024 -> TOP_512)
        This only works if the stage is not the last stage (FINISHED) or one of the special cases indicated by the negative enum values (PRELIMINARY_ROUND, PLACEMENTS)
        Returns
        -------
        Stage (-1)
        """
        if self.value >= 1:
            return Stage(self.value - 1)
        
    def previous_stage(self):
        """
        Decreases the stage by one (e.g. TOP_512 -> TOP_1024)
        This only works if the stage is not the first stage (PRELIMINARY_ROUND) or one of the special cases indicated by the negative enum values (PLACEMENTS)
        Returns
        -------
        Stage (-1)
        """
        if self.value <= 9:
            return Stage(self.value + 1)

    @property
    def short_stage_name(self):
        """
        Returns the name of the stage in a short format (e.g. "QF" instead of "QUARTER_FINALS")
        """
        if self.value == -1:
            return "G"
        elif self.value == -2:
            return "P"

        elif self.value == 10:
            return "1024th"
        elif self.value == 9:
            return "512th"
        elif self.value == 8:
            return "256th"
        elif self.value == 7:
            return "128th"
        elif self.value == 6:
            return "64th"
        elif self.value == 5:
            return "32nd"
        elif self.value == 4:
            return "16th"
        elif self.value == 3:
            return "QF"
        elif self.value == 2:
            return "SF"
        elif self.value == 1:
            return "GF"
        elif self.value == 0:
            return "Finished"



# Main Class for every individual fencer
class Fencer:
    """
    Main Class for every individual fencer. When creating the tournament, a csv file is read and a list of Fencer objects is created.
    The Fencer class contains all basic information about the fencer, such as name, club and nationailty, but also 
    information about the tournament, matches and statistics.

    The fencer class is the main source for the fencer's hub-page, where every individual fencer can see his/her statistics and matches.
    """

    def __init__(self, name: str, club: str = None, nationailty: str = None, gender: Literal["M", "F", "D"] = None, handedness: Literal["R", "L"] = None, age: int = None, start_number: int = None, num_prelim_rounds: int = 1):
        """
        Constructor for the Fencer class

        Parameters
        ----------
        name : str
            The name of the fencer (Sur- and Firstname are one string)
        club : str, optional
            The club the fencer is associated with (preferrably only an acronym or abbreviation), by default None
        nationailty : str, optional
            The nationailty of the fencer, by default None

            Note
            ----
            Preferably only use the alpha-3 Code e.g. GER for Germany or FRA for France.
            The full (english) name works as well, since it is cross referenced in :meth:`__init__`, but is not recommended
        gender : str, optional
            The gender of the fencer, by default None, can be either "M", "F" or "D"
        handedness : str, optional
            The handedness of the fencer, by default None, can be either "R" or "L"

        start_number : int, optional
            The start number of the fencer, by default None

            Note
            ----
            Since the start number is assigned automatically later anyways, it is not necessary to provide it here

        num_prelim_rounds : int, optional
            The number of preliminary rounds, by default 1, important for statistics
        
        Attributes
        ----------
        self.id : str
            The unique id of the fencer, generated by the :meth:`random_generator.id` function
        self.start_number : int
        self.name : str
        self.club : str
        self.nationality : len(3) str
            Alpha-3 country code
        self.gender : str
            Holds the gender of the fencer, either "M" for male, "F" for female or "D" for divers
        self.handedness : str
            Holds the handedness of the fencer, either "R" for right handed or "L" for left handed
        self.prelim_group : int
            Holds the group number the fencer is in
            Variable assigned when the preliminary round is created
        self.elimination_value : int
            Holds an index for the final ranking
            When a fencer loses a match in "KO" mode, the elimination value is the current stage.
            In "Placement" mode, the index is only assigned at the very last match of the tournament in accordance to his/her performance in the elimination round
        self.last_match_won : bool
            Holds the information if the fencer won his/her last match.

            Note
            ----
            TODO This can also be an array, holding the whole fencers history

        self.group_opponents : list of Fencer
            Holds the opponents the fencer has faced in the preliminary round, used for repechage

            Note
            ----
            Since repechage is not implemented yet, this is not used yet

        self.stage : Stage
            Keeps track of the Stage the fencer is in
        self.eliminated : bool
            Tracks whether the fencer has been eliminated from the direct elimination round or not
        self.final_rank : int
            Holds the final rank of the fencer
            This is only assigned at the very end of the tournament
        self.statistics : dict
            This dictionary holds all relevant statistics in any stage.
            It tracks matches, wins, losses, points_for, points_against in all preliminary rounds, the elimination round and overall.
            The keys are: "overall", "elimination" and "preliminary_round" (last is a list of all preliminary rounds)
        


        

        """
        # ID
        self.id = id(10)

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

        self.gender: Literal["M", "F", "D"] = gender

        self.handedness: Literal["R", "L"] = handedness

        self.age: int = age

        self.push_notification_tokens = [] # This is used for push notifications

        self.disqualified = False
        self.disq_save_nationality = None # This stores the nationality of the fencer in case he/she is disqualified
        self.disq_reason = None # This stores the reason for disqualification


        # Grouping information
        self.prelim_group = None

        # Elimination Value
        self.elimination_value = None # This Index is used for calculating the next opponent in the elimination stage

        # Past opponents (for repechage)
        self.group_opponents = [] # This is needed for matchmaking in the direct elimination stage when repechage is used.

        # Stage information
        self.in_match = False # Tracks if the fencer is currently in a match
        self.is_staged = False # Tracks if the fencer is staged for a match
        self.stage: Stage = Stage.PRELIMINARY_ROUND # Tracks the advancement of the fencer (to determine standings)
        self.eliminated = False # Tracks if the fencer has been eliminated from the tournament

        # Approved of last tableau
        self.approved_tableau = False

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

        self.last_matches: list = []

        self.game_lables: list = ["Start"]
        self.standings_history: list = [start_number]
        self.difference_history: list = []
        self.difference_per_match_history: list = []

        for _ in range(num_prelim_rounds):
            self.statistics["preliminary_round"].append({
                "matches": 0,
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0
            })

        # Cookies
        self.cookies = []




    def __str__(self) -> str:
        """
        Returns a string representation of the fencer depending on the information available

        Returns
        -------
        Start Number Name : str
        Start Number Name (Nationailty) : str
        Start Number Name / Club : str
        Start Number Name (Nationailty) / Club : str

        """
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
        """
        ``@property``

        Returns a short string representation of the fencer consisting of start number and name

        Returns
        -------
        Start Number (3x Space) Name : str
        """
        return f"{self.start_number}   {self.name}"

    @property
    def last_match_won(self):
        if len(self.last_matches) == 0:
            return None
        else:
            return self.last_matches[-1]["win"]

    @property
    def outcome_last_matches(self) -> list:
        """
        ``@property``

        Returns a list of the last 5 matches of the fencer

        Returns
        -------
        List of 5 bools
        """
        return [match["win"] for match in self.last_matches][-8:]


    def match_started(self):
        self.in_match = True
        self.is_staged = False

    def disqualify(self, reason: str = None):
        self.disqualified = True
        self.disq_save_nationality = self.nationality
        self.nationality = "DQD"
        self.disq_reason = reason
    
    def revoke_disqualification(self):
        self.disqualified = False
        self.nationality = self.disq_save_nationality
        self.disq_save_nationality = None

    def subscribe_to_push_notifications(self, token: str):
        if token not in self.push_notification_tokens:
            self.push_notification_tokens.append(token)

    def unsubscribe_from_push_notifications(self, token: str):
        try:
            self.push_notification_tokens.remove(token)
        except ValueError:
            pass


    # statistics
    def update_statistics(self, match, win: bool, opponent, points_for: int, points_against: int, round: int = 0, skip_last_matches: bool = False) -> None:
        """
        This function updates the statistics of the fencer and is called after every match is finished and the score has been pushed.
        The function updates the statistics for the current stage and the overall statistics.

        Parameters
        ----------
        match : Match
            The match object of the match that was played
        win : bool
            Whether the fencer won the match or not
        opponent : Fencer
            The opponent of the fencer
        points_for : int
            The points the fencer scored in the match
        points_against : int
            The points the opponent scored in the match
        round : int
            The round the match was played in (default: 0)
        """
        if self.stage == Stage.PRELIMINARY_ROUND:
            stage = self.stage.name.lower()
        else:
            stage = "elimination"

        if not skip_last_matches:
            self.last_matches.append({
                "win": win,
                "opponent": opponent.id,
                "match": match.id,
            })

        if win:
            self.statistics["overall"]["wins"] += 1
            self.statistics[stage][round]["wins"] += 1
        else:
            self.statistics["overall"]["losses"] += 1
            self.statistics[stage][round]["losses"] += 1

        self.statistics["overall"]["matches"] += 1
        self.statistics["overall"]["points_for"] += points_for
        self.statistics["overall"]["points_against"] += points_against

        self.statistics[stage][round]["matches"] += 1
        self.statistics[stage][round]["points_for"] += points_for
        self.statistics[stage][round]["points_against"] += points_against

        self.group_opponents.append(opponent)

        self.game_lables.append("Group" if self.stage == Stage.PRELIMINARY_ROUND else self.stage.short_stage_name)
        self.difference_history.append(self.points_difference_int())
        self.difference_per_match_history.append(points_for - points_against)


    def correct_statistics(self, match, opponent, old_points_for: int, old_points_against: int, points_for: int, points_against: int, round: int = 0):
        if self.stage == Stage.PRELIMINARY_ROUND:
            stage = self.stage.name.lower()
        else:
            stage = "elimination"

        if old_points_for > old_points_against:
            self.statistics["overall"]["wins"] -= 1
            self.statistics[stage][round]["wins"] -= 1
        else:
            self.statistics["overall"]["losses"] -= 1
            self.statistics[stage][round]["losses"] -= 1

        self.statistics["overall"]["matches"] -= 1
        self.statistics["overall"]["points_for"] -= old_points_for
        self.statistics["overall"]["points_against"] -= old_points_against

        self.statistics[stage][round]["matches"] -= 1
        self.statistics[stage][round]["points_for"] -= old_points_for
        self.statistics[stage][round]["points_against"] -= old_points_against

        if points_for > points_against:
            win = True
        else:
            win = False

        for entry in self.last_matches:
            if entry["match"] == match.id:
                entry["win"] = win
        
        self.update_statistics(match, win, opponent, points_for, points_against, round, skip_last_matches=True)


    
    def update_statistics_wildcard_or_disq_game(self, match, disq: bool = False):
        self.last_matches.append({
            "win": True,
            "opponent": "Wildcard" if not disq else "Disqualified Opponent",
            "match": match.id,
        })

    def update_rank(self, rank: int) -> None:
        self.standings_history.append(rank)


    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> int:
        """
        Calculates the Win Percentage of the fencer for a given stage

        Note
        ----
        The Win Percentage is the first parameter used for determining the standings of the fencer in the preliminary stage

        Parameters
        ----------
        stage : Literal["overall", "preliminary", "intermediate", "elimination"]
            The stage for which the win percentage should be calculated (default: "overall")
        
        Returns
        -------
        Win Percentage : int

            Note
            ----
            The win percentage is multiplied by 100 and rounded to the nearest integer.
        """
        return int(round((self.statistics[stage]["wins"]*1.0) / (self.statistics[stage]["matches"]*1.0)*100) if self.statistics[stage]["matches"] != 0 else 0)

    def points_difference_int(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> int:
        """
        Calculates the Points Difference of the fencer for a given stage.
        The Points Difference is calculated by subtracting the points against from the points for.

        Note
        ----
        The Points Difference is the second parameter after the win percentage used for determining the standings of the fencer in the preliminary stage

        Parameters
        ----------
        stage : Literal["overall", "preliminary", "intermediate", "elimination"]
            The stage for which the points difference should be calculated (default: "overall")

        Returns
        -------
        Points Difference : int
        """
        difference = self.statistics[stage]["points_for"] - self.statistics[stage]["points_against"]
        return int(difference)

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> str:
        """
        See :meth:`points_difference_int`, but returns a string with a "+" in front of the points difference if it is positive, with a "-" if it is negative and nothing if it is 0.

        Returns
        -------
        Points Difference : str
        """
        difference = self.points_difference_int(stage)
        return str("+" + str(difference) if difference > 0 else str(difference))

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        """
        Calculates the Points per Game of the fencer for a given stage.
        The Points per Game is calculated by dividing the points for by the number of matches.

        Parameters
        ----------
        stage : Literal["overall", "preliminary", "intermediate", "elimination"]
        
        Returns
        -------
        Points per Game : float
        """
        return (round(self.statistics[stage]["points_for"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall") -> float:
        """
        Calculates the Points against per Game of the fencer for a given stage.

        Parameters
        ----------
        stage : Literal["overall", "preliminary", "intermediate", "elimination"]

        Returns
        -------
        Points against per Game : float
        """
        return (round(self.statistics[stage]["points_against"] / self.statistics[stage]["matches"], 2) if self.statistics[stage]["matches"] != 0 else 0)

    
    def change_attribute(self, attribute: Literal["name", "club", "nationality", "gender", "handedness", "age"], value):
        # Assign the new value to the attribute of the Fencer class
        check_attr(attribute, value)

        try:
            if getattr(self, attribute) == value:
                raise ValueError(f"Attribute {attribute} already has the value {value}")
            setattr(self, attribute, value)
        except AttributeError:
            raise AttributeError(f"Attribute {attribute} does not exist")



class Wildcard(Fencer):
    """
    The Wildcard class is a subclass of the Fencer class and represents a "Placeholder" fencer that is used to fill up the number of fencers in the elimination Stage to a multiple of 4.
    
    Note
    ----
    Main purpose is to signal to the :class:`Match`, that the fencer is a wildcard and that the :class:`fencer.Fencer` Opponent wins instantly 1:0. Also, there will be no :meth:`fencer.Fencer.update_statistics` call to update the :class:`fencer.Wildcard` or the Opponent :class:`fencer.Fencer`.
    """
    def __init__(self, wildcard_number: int):
        """
        Parameters
        wildcard_number : int
            The number of the wildcard. Used to distinguish between different wildcards.
            Could be seen as the equivalent to the :class:`fencer.Fencer.start_number`
        """
        super().__init__("Wildcard", nationailty="WLD")
        self.wildcard_number = wildcard_number
        self.start_number = 0

    @property
    def last_match_won(self):
        return False

    def points_against_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        """
        See :meth:`fencer.Fencer.points_against_per_game`, but raises a TypeError, because the :class:`fencer.Wildcard` has no statistics like a normal fencer.

        Raises
        ------
        TypeError
            "Wildcard has no statistics like a normal fencer"
        """
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def points_per_game(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        """
        See :meth:`fencer.Fencer.points_per_game`, but raises a TypeError, because the :class:`fencer.Wildcard` has no statistics like a normal fencer.

        Raises
        ------
        TypeError
            "Wildcard has no statistics like a normal fencer"
        """
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def points_difference(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        """
        See :meth:`fencer.Fencer.points_difference`, but raises a TypeError, because the :class:`fencer.Wildcard` has no statistics like a normal fencer.

        Raises
        ------
        TypeError
            "Wildcard has no statistics like a normal fencer"
        """
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def win_percentage(self, stage: Literal["overall", "preliminary", "intermediate", "elimination"] = "overall"):
        """
        See :meth:`fencer.Fencer.win_percentage`, but raises a TypeError, because the :class:`fencer.Wildcard` has no statistics like a normal fencer.

        Raises
        ------
        TypeError
            "Wildcard has no statistics like a normal fencer"
        """
        raise(TypeError("Wildcard has no statistics like a normal fencer"))

    def update_statistics(self, win: bool, opponent, points_for: int, points_against: int, round: int = 0):
        """
        See :meth:`fencer.Fencer.update_statistics`, but raises a TypeError, because the :class:`fencer.Wildcard` has no statistics like a normal fencer and cannot not be updated.

        Raises
        ------
        TypeError
            "Wildcard has no statistics like a normal fencer"
        """
        raise(TypeError("Wildcard has no statistics like a normal fencer"))