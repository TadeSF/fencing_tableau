from fencer import Fencer

class Match:
    id = 1
    def __init__(self, fencer_green: Fencer, fencer_red: Fencer, fencing_piste: int = None, elimination: bool = False):
        # ID
        self.id = Match.id
        Match.id += 1

        # Match information
        self.match_number = None
        self.elimination = elimination
        self.piste = fencing_piste
        self.match_completed = False

        # Fencer Information
        self.green = fencer_green
        self.red = fencer_red

        # Score
        self.green_score = 0
        self.red_score = 0

    
    def __str__(self) -> str:
        if self.match_completed:
            return_str = self.score
        else:
            return_str = f"Match {self.id}:   {self.green.short_str()} vs. {self.red.short_str()}   (Piste {self.piste})"
        return return_str


    # Statistics
    @property
    def score(self) -> str:
        return f"Match {self.id} Result:   {self.green.short_str().upper() if self.green == self.winner else self.green.short_str()}   {self.green_score}:{self.red_score}   {self.red.short_str().upper() if self.red == self.winner else self.red.short_str()}   (Piste {self.piste})"

    @property
    def winner(self) -> Fencer:
        if self.green_score > self.red_score:
            return self.green
        elif self.red_score > self.green_score:
            return self.red
        else:
            return None
    
    @property
    def loser(self) -> Fencer:
        if self.green_score < self.red_score:
            return self.red
        elif self.red_score > self.green_score:
            return self.green
        else:
            return None

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
