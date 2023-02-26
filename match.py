import random
from typing import Literal

from fencer import Fencer, Stage, Wildcard
from piste import Piste
import random_generator
from datetime import datetime
import logging

# ------- Logging -------
try: # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('match')
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


class Match:

    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, stage: Stage, fencing_piste: Piste = None):

        # ID
        self.id = random_generator.id(12)
        self.sorting_id = self.id
        
        # Group
        self.group = None

        # Match information
        self.piste: Piste = None
        self.priority = 0
        self.match_ongoing = False
        self.match_ongoing_timestamp: datetime = None
        self.match_completed = False
        self.match_completed_timestamp: datetime = None
        self.wildcard = False

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Stage information
        self.stage = stage

        # Score
        self.green_score = 0
        self.red_score = 0

        # Logging
        logger.info(f"Match created: {self.id}, {self.green.name} - {self.red.name}")

    
    def __getitem__(self, index: Literal["green", "red"]):
        if index == "green":
            return self.green
        elif index == "red":
            return self.red
        else:
            raise KeyError("Invalid key")


    def __iter__(self):
        return iter([self.green, self.red])

    def to_dict(self):
        return {
            "id": self.id,
            "sorting_id": self.sorting_id,
            "group": self.group,
            "piste": self.piste,
            "match_ongoing": self.match_ongoing,
            "match_completed": self.match_completed,
            "wildcard": self.wildcard,
            "green": self.green,
            "red": self.red,
            "stage": self.stage,
            "green_score": self.green_score,
            "red_score": self.red_score
        }

    # Statistics
    @property
    def winner(self) -> Fencer:
        if self.green_score > self.red_score:
            return self.green
        elif self.red_score > self.green_score:
            return self.red
        else:
            raise ValueError("No winner yet")
    
    @property
    def loser(self) -> Fencer:
        if self.green_score > self.red_score:
            return self.red
        elif self.red_score > self.green_score:
            return self.green
        else:
            raise ValueError("No loser yet")

    @property
    def piste_str(self) -> str:
        if self.piste != None:
            return str(self.piste.number) 
        elif self.wildcard:
            return "-"
        else:
            return "TBA"


    # Input Results
    def input_results(self, green_score: int, red_score: int) -> None:
        # Check for invalid score
        if green_score < 0 or red_score < 0:
            raise ValueError("Score must be a positive integer")
        elif green_score == red_score:
            raise ValueError("Score must be different")

        # Valid score
        else:
            self.green_score = green_score
            self.red_score = red_score
            self.green.in_match = False
            self.red.in_match = False
            self.match_ongoing = False
            self.match_completed = True
            self.match_completed_timestamp = datetime.now()

            # Free Piste
            try:
                self.piste.match_finished()
            except AttributeError: # Piste is None, happens when wildcard. # TODO: Look into this
                pass


    def set_active(self, staged: bool = False):
        self.piste.match_started(staged)
        self.green.match_started()
        self.red.match_started()
        self.match_ongoing = True
        self.match_ongoing_timestamp = datetime.now()

    def assign_piste(self, piste: Piste):
        self.piste = piste
        self.piste.staged = True
        self.green.is_staged = True
        self.red.is_staged = True



class GroupMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, stage: Stage, fencing_piste: Piste = None, group: str = None, prelim_round: int=0):
        super().__init__(fencer_green, fencer_red, stage, fencing_piste)
        self.group = group
        self.prelim_round = prelim_round

    def input_results(self, green_score: int, red_score: int, skip_update_statistics: bool = False) -> None:
        super().input_results(green_score, red_score)

        if not skip_update_statistics:
            self.green.update_statistics(self, True if self.winner == self.green else False, self.red, self.green_score, self.red_score, round=self.prelim_round)
            self.red.update_statistics(self, False if self.winner == self.green else True, self.green, self.red_score, self.green_score, round=self.prelim_round)




class EliminationMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, stage: Stage, fencing_piste: Piste = None):
        super().__init__(fencer_green, fencer_red, stage, fencing_piste)

        if self.green.name == "Wildcard":
            self.match_completed = True
            self.red_score = 1
            self.wildcard = True
            self.red.update_statistics_wildcard_game(self)
        elif self.red.name == "Wildcard":
            self.match_completed = True
            self.green_score = 1
            self.wildcard = True
            self.green.update_statistics_wildcard_game(self)

    def input_results(self, green_score: int, red_score: int, skip_update_statistics: bool = False) -> None:
        super().input_results(green_score, red_score)

        if not skip_update_statistics:
            self.green.update_statistics(self, True if self.winner == self.green else False, self.red, self.green_score, self.red_score)
            self.red.update_statistics(self, False if self.winner == self.green else True, self.green, self.red_score, self.green_score)