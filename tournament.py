import math
from fencer import *
from match import *

from typing import Literal, List


# ------- Groups -------

def assign_groups(fencers: list[Fencer], groups: int = None) -> list[list[Fencer]]:

    # TODO – Implement the following rules of the Deutscher Fechter-Bund for the preliminary tableau:
    ''' Eine aktuelle Landesrangliste oder deutsche Rangliste hilft uns,
    die Turnierfavoriten gleichmäßig auf die Gruppen zu verteilen.
    Außerdem sollte nie mehr als ein Fechter vom selben Verein
    (bei internationalen Turnieren aus demselben Land) in einer Gruppe sein.
    Das geht natürlich nicht immer. Wenn wir zehn Gruppen haben,
    aber einen Verein mit zwölf Teilnehmern, dann wird es eben zwei Gruppen geben,
    wo je zwei Vereinskollegen zusammen fechten.
    Die müssen dann aber das allererste Gefecht gegeneinander machen.'''

    # if groups is None, calculate the optimal number of groups
    if groups is None:
        # Calculate the number of preliminary groups
        # All Groups should have the same number of fencers
        # In the best case, there should be a maximum of 8 fencers per group.
        # The number of groups should be as low as possible
        if len(fencers) < 8:
            num_of_groups = 1
        else:
            num_of_groups = len(fencers) // 8
            if len(fencers) % 8 > 0:
                num_of_groups += 1


    # Assign groups to fencers (randomly, but (hopefully) evenly distributed)
    # TODO – In the best case, there should be no fencers from the same club in the same group

    grouping = [[] for _ in range(0, num_of_groups)]

    # Assign groups to fencers
    counter = 1
    for i in range(0, len(fencers)):
        if fencers[i].stage == Stage.PRELIMINARY_ROUND:
            fencers[i].prelim_group = counter
            grouping[counter - 1].append(fencers[i])
        elif fencers[i].stage == Stage.INTERMEDIATE:
            fencers[i].intermediate_group = counter
            grouping[counter - 1].append(fencers[i])
        counter += 1
        if counter > num_of_groups:
            counter = 1
    
    return grouping


# ------- Matchmaking Logic -------

def matchmaker_groups(fencers: list[Fencer]) -> list[Match]:
    # Create matchups
    matches = []

    # Every fencer fences against every other fencer
    for i in range(0, len(fencers)):
        for j in range(i + 1, len(fencers)):
            matches.append(Match(fencers[i], fencers[j]))

    return matches


def matchmaker_elimination(fencers: list, mode: Literal["ko", "repechage", "placement"]) -> list[Match]:
    # Create matchups
    matches = []

    if mode == "ko" or mode == "placement":
        for group in fencers:
            for j in range(int(len(group) / 2)):
                # Create match
                # The first fencer fences against the last fencer, the second fencer fences against the second last fencer, etc.
                matches.append(Match(group[j], group[-j]))

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode

    return matches


# ------- Tournament Logic -------

# Creating matches in group stages (preliminary and intermediate)
def create_group_matches(fencers: List[List[Fencer]], groups: int = None) -> list[Match]:
    # Create groups
    groups = assign_groups(fencers, groups)

    # Create matches
    matches = []
    for group in groups:
        matches.append(matchmaker_groups(group))
    
    return matches


# ------- Sorting Algorithms -------

# Sorting for Standings and Advanced to next round
def sorting_fencers(fencers: list[Fencer]) -> list[Fencer]:
    # Sort fencers by overall score
    # sort by stage, win percentage, points difference, points for, points against
    fencers = sorted(fencers, key=lambda fencer: (fencer.stage, fencer.win_percentage(), fencer.points_difference(), fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"]), reverse=True)

    return fencers


# Algorithm to set up next tree node (for the elimination tree)
def next_tree_node(sorted_list: List[List[Fencer]], mode: Literal["ko", "repechage", "placement"] = "ko") -> list:

    transposed_list = []

    if mode == "ko" or mode == "placement":
        # Iterate over the sublists
        for sublist in sorted_list:      # in this for loop, the var sublist is a list of fencers

            advanced = []               # List to temporarily store the advanced fencers
            eliminated = []             # List to temporarily store the eliminated fencers

            # Iterate over the elements in the sublist
            for i in range(len(sublist)):
                
                if i < len(sublist) / 2:            # If the index of the fencer is in the first half of the list
                    advanced.append(sublist[i])     # Add the fencer to the advanced list
                else:                               # else
                    eliminated.append(sublist[i])   # Add the fencer to the eliminated list

            # Add the advanced and eliminated lists to the transposed list in the correct order (advanced first, then eliminated)
            transposed_list.append(advanced)
            if mode == "placement": transposed_list.append(eliminated) # If the mode is ko, the eliminated list is not added to the transposed list. All losers are eliminated.
    

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode      

    else:
        raise ValueError("Mode not supported")

    # Return the transposed list
    return transposed_list
    





# ------- Tournament Class -------

class Tournament:

    def __init__(
        self,
        name: str,
        fencers: list[Fencer],
        location: str = None,
        date: str = None,
        num_preliminary_rounds: int = 1,
        num_preliminary_groups: int = None,
        max_elimination_rounds: int = None,
        elimination_mode: Literal["ko", "repechage", "placement"] = "ko",
        only_elimination: bool = False,
        ):

        # Name of the tournament
        self.name = name
        
        # Location and date of the tournament
        self.location = location
        self.date = date

        # List of fencers in the tournament
        self.fencers = fencers

        # Custumizable tournament procedures
        self.num_preliminary_rounds = num_preliminary_rounds
        self.num_preliminary_groups = num_preliminary_groups
        self.max_elimination_rounds = max_elimination_rounds
        self.elimination_mode = elimination_mode
        self.only_elimination = only_elimination

        # --------------------

        # List of fencers in the preliminary round
        self.preliminary_fencers = []
        self.preliminary_matches = []

        # List of fencers in the elimination round
        self.elimination_fencers = [[]]
        self.elimination_matches = []

        # Stage of the tournament
        self.elimination_first_stage = Stage(math.ceil(math.log2(len(fencers)))) if self.max_elimination_rounds == None else Stage(self.max_elimination_rounds)
        self.stage: Stage = Stage.PRELIMINARY_ROUND if not self.only_elimination else self.elimination_first_stage


    def create_preliminary_round(self) -> None:
        # Create preliminary round
        self.preliminary_fencers = self.fencers
        self.preliminary_matches = create_group_matches(self.preliminary_fencers)

    def create_next_elimination_round(self) -> None:
        # Create next (or first) elimination round

        # If it is the first elimination round, sort the fencers by overall score and append them to the elimination fencers list
        if self.elimination_matches == []:
            self.elimination_fencers = [sorting_fencers(self.fencers)]
            if self.max_elimination_rounds != None:
                self.elimination_fencers = self.elimination_fencers[(self.max_elimination_rounds ** 2):] # TODO Continue here
        else:
            self.elimination_fencers = next_tree_node(self.elimination_fencers, self.elimination_mode)

        self.elimination_matches = matchmaker_elimination(self.elimination_fencers, self.elimination_mode)


    def get_standings(self) -> dict:
        # Get current standings and return them as a dictionary for the GUI
        standings = {
            "stage": self.stage.name,
            "standings": [],
        }

        # Sort fencers by overall score
        fencers = sorting_fencers(self.fencers)

        for fencer in fencers:
            standings["standings"].append({
                "rank": fencers.index(fencer) + 1,
                "name": fencer.name,
                "club": fencer.club,
                "nationality": fencer.nationality,
                "win_percentage": fencer.win_percentage(),
                "win_lose": f"{fencer.statistics['overall']['wins']} - {fencer.statistics['overall']['losses']}",
                "points_difference": fencer.points_difference(),
                "points_for": fencer.statistics["overall"]["points_for"],
                "points_against": fencer.statistics["overall"]["points_against"],
            })

        return standings

    def get_matches(self) -> dict:
        if self.stage == Stage.PRELIMINARY_ROUND:
            dictionary = {
                "stage": self.stage.name,
                "matches": [],
            }
            for group in self.preliminary_matches:
                for match in group:
                    dictionary["matches"].append({
                        "id": match.id,
                        # Calculate "group" by getting the index of the group in the list of groups and adding 1
                        "group": self.preliminary_matches.index(group) + 1,
                        "piste": match.piste,
                        "green": match.green.name,
                        "green_nationality": match.green.nationality,
                        "green_score": match.green_score,
                        "red": match.red.name,
                        "red_nationality": match.red.nationality,
                        "red_score": match.red_score,
                        "ongoing": match.match_ongoing,
                        "complete": match.match_completed
                    })
            return dictionary

        elif self.stage == Stage.INTERMEDIATE:
            dictionary = {
                "stage": self.stage.name,
                "matches": [],
            }
            for match in self.preliminary_matches:
                dictionary["matches"].append({
                    "id": match.id,
                    "group": match.green.intermediate_group,
                    "piste": match.piste,
                    "green": match.green,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red,
                    "red_nationality": match.green.nationality,
                    "red_score": match.red_score,
                    "complete": match.match_completed
                })
            return dictionary
        else:
            dictionary = {
                "stage": self.stage.name,
                "matches": [],
            }
            for match in self.preliminary_matches:
                dictionary["matches"].append({
                    "id": match.id,
                    "piste": match.piste,
                    "green": match.green,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red,
                    "red_nationality": match.green.nationality,
                    "red_score": match.red_score,
                    "complete": match.match_completed
                })
            return dictionary


    def generate_matches(self) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.create_preliminary_round()

        elif self.stage == Stage.INTERMEDIATE:
            self.create_intermediate_round()

        else:
            raise NotImplementedError # TODO: Implement elimination round


    def push_score(self, match_id: int, green_score: int, red_score: int) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND or self.stage == Stage.INTERMEDIATE:
            for group in (self.preliminary_matches + self.intermediate_matches):
                for match in group:
                    if match.id == match_id:
                        match.input_results(green_score, red_score)

        else:
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.input_results(green_score, red_score)


    def set_active(self, match_id: int) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND or self.stage == Stage.INTERMEDIATE:
            for group in (self.preliminary_matches + self.intermediate_matches):
                for match in group:
                    if match.id == match_id:
                        match.set_active()

        else:
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.set_active()