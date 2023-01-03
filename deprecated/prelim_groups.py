import itertools
import random
from match import Match
from fencer import Fencer

class PreliminaryGroup:
    def __init__(self, fencers: list, group_number: int) -> None:

        # Group information
        self.group_number = group_number
        self.group_completed = False

        self.fencers = fencers
        self.matches = []

        self.standings = None


    def calculate_standings(self) -> None:
        self.standings = self.fencers
        self.standings.sort(key=lambda fencer: (fencer.win_percentage, fencer.points_difference, fencer.points_for, fencer.points_against), reverse=True)
        self.group_completed = True


    @property
    def group_letter(self) -> str:
        return str(chr(self.group_number + 64))

    @property
    def number_of_fenceres(self) -> int:
        return len(self.fencers)

    @property
    def number_of_matches(self) -> int:
        return len(self.matches)

    @property
    def combinations(self) -> list:
        combinations = list(itertools.combinations(self.fencers, 2))
        random.shuffle(combinations)
        return combinations

