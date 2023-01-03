import random
from typing import Literal
from fencer import Fencer, Wildcard, Stage


class Match:

    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int = None):

        # ID
        self.id = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))

        # Match information
        self.piste = fencing_piste
        self.match_ongoing = False
        self.match_completed = False

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Score
        self.green_score = 0
        self.red_score = 0


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
            self.match_ongoing = False
            self.match_completed = True
        
            # Update statistics
            self.green.update_statistics(True if self.winner == self.green else False, self.red, self.green_score, self.red_score)
            self.red.update_statistics(False if self.winner == self.green else True, self.green, self.red_score, self.green_score)

    def set_active(self):
        self.match_ongoing = True


class GroupMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, group_number = None, fencing_piste: int = None):
        super().__init__(fencer_green, fencer_red, fencing_piste)
        self.group_number = group_number


class EliminationMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int = None):
        super().__init__(fencer_green, fencer_red, fencing_piste)

        # If the match is a wildcard match, the other fencer is automatically the winner
        self.wildcard = False

        if self.green.name == "Wildcard":
            self.match_completed = True
            self.red_score = 1
            self.wildcard = True
        elif self.red.name == "Wildcard":
            self.match_completed = True
            self.green_score = 1
            self.wildcard = True