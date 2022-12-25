import random
from typing import Literal
from fencer import Fencer, Wildcard


class Match:
    id = 1
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int = None):
        # ID
        self.id = Match.id
        Match.id += 1

        # Match information
        self.piste = fencing_piste
        self.match_completed = False
        self.wildcard = False

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Score
        self.green_score = 0
        self.red_score = 0

        # If the match is a wildcard match, the other fencer is automatically the winner
        if self.green.name == "Wildcard":
            self.match_completed = True
            self.red_score = 1
            self.wildcard = True
        elif self.red.name == "Wildcard":
            self.match_completed = True
            self.green_score = 1
            self.wildcard = True

    
    def __str__(self) -> str:
        if self.match_completed:
            return_str = self.score
        else:
            return_str = f"Match {self.id}:   {self.green.short_str()} vs. {self.red.short_str()}   Piste {self.piste}"
        return return_str


    # Statistics
    @property
    def score(self) -> str:
        return_str = f"Match {self.id} Result:   {self.green.short_str().upper() if self.green == self.winner else self.green.short_str()}   {self.green_score}:{self.red_score}   {self.red.short_str().upper() if self.red == self.winner else self.red.short_str()}   Piste {self.piste}"
        return return_str

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
            self.match_completed = True
        
            # Update statistics
            self.green.update_statistics(True if self.winner == self.green else False, self.green_score, self.red_score)
            self.red.update_statistics(False if self.winner == self.green else True, self.red_score, self.green_score)


class GroupMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, prelim_group = None, fencing_piste: int = None):
        super().__init__(fencer_green, fencer_red, fencing_piste)
        self.group_number = prelim_group

    def __str__(self) -> str:
        return_str = super().__str__()
        return_str += f"   Group {self.group_number.group_letter}"
        return return_str

    @property
    def score(self) -> str:
        return_str = super().score
        return_str += f"   Group {self.group_number.group_letter}"
        return return_str




class EliminationMatch(Match):
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, elimination_round: Literal["32th", "16th", "QF", "SF", "P3", "Final"] = None, fencing_piste: int = None):
        super().__init__(fencer_green, fencer_red, fencing_piste)
        self.elimination_round = elimination_round

    def input_results(self, green_score: int, red_score: int):
        super().input_results(green_score, red_score)

    def __str__(self) -> str:
        return_str = f"{self.elimination_round}: "
        return_str += super().__str__()
        return return_str

    @property
    def score(self) -> str:
        return_str = f"{self.elimination_round}: "
        return_str += super().score
        return return_str