from fencer import *
from match import *

from typing import Literal


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
        if fencers[i].stage == Stage.PRELIMINARY:
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


def matchmaker_elimination(fencers: list[Fencer], mode: Literal["ko", "repechage", "placement"]) -> list[Match]:
    # Create matchups
    matches = []
    if mode == "ko":
        for i in range(0, len(fencers) / 2):
            # Create match
            # The first fencer fences against the last fencer, the second fencer fences against the second last fencer, etc.
            matches.append(Match(fencers[i], fencers[-i]))

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode
    elif mode == "placement":
        raise NotImplementedError("Placement mode not implemented yet") # TODO implement placement mode
    
    return matches


# ------- Tournament Logic -------

# Creating matches in group stages (preliminary and intermediate)
def create_group_matches(fencers: list[Fencer], groups: int = None) -> list[Match]:
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

    





# ------- Tournament Class -------

class Tournament:

    def __init__(
        self,
        name: str,
        fencers: list[Fencer],
        location: str = None,
        date: str = None,
        elemination_rounds: int = 5,
        elemination_mode: Literal["ko", "repechage", "placement"] = "ko",
        only_elimination: bool = False,
        no_intermediate: bool = False,
        ):

        # Name of the tournament
        self.name = name
        
        # Location and date of the tournament
        self.location = location
        self.date = date

        # List of fencers in the tournament
        self.fencers = fencers

        # Custumizable tournament procedures
        self.elemination_rounds = elemination_rounds
        self.elemination_mode = elemination_mode
        self.only_elimination = only_elimination
        self.no_intermediate = no_intermediate

        # --------------------

        # List of fencers in the preliminary round
        self.preliminary_fencers = []
        self.preliminary_matches = []
        
        # List of fencers in the intermediate round
        self.intermediate_fencers = []
        self.intermediate_matches = []

        # List of fencers in the elimination round
        self.elimination_fencers = []
        self.elimination_matches = []

        # Stage of the tournament
        self.stage: Stage = Stage.PRELIMINARY if not only_elimination else Stage(self.elemination_rounds)


    def create_preliminary_round(self) -> None:
        # Create preliminary round
        self.preliminary_fencers = self.fencers
        self.preliminary_matches = create_group_matches(self.preliminary_fencers)

    def create_intermediate_round(self) -> None:
        # Create intermediate round
        self.intermediate_fencers = self.fencers[:48]
        self.intermediate_matches = create_group_matches(self.intermediate_fencers)




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
        if self.stage == Stage.PRELIMINARY:
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
        if self.stage == Stage.PRELIMINARY:
            self.create_preliminary_round()

        elif self.stage == Stage.INTERMEDIATE:
            self.create_intermediate_round()

        else:
            raise NotImplementedError # TODO: Implement elimination round


    def push_score(self, match_id: int, green_score: int, red_score: int) -> None:
        if self.stage == Stage.PRELIMINARY or self.stage == Stage.INTERMEDIATE:
            for group in (self.preliminary_matches + self.intermediate_matches):
                for match in group:
                    if match.id == match_id:
                        match.input_results(green_score, red_score)

        else:
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.input_results(green_score, red_score)


    def set_active(self, match_id: int) -> None:
        if self.stage == Stage.PRELIMINARY or self.stage == Stage.INTERMEDIATE:
            for group in (self.preliminary_matches + self.intermediate_matches):
                for match in group:
                    if match.id == match_id:
                        match.set_active()

        else:
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.set_active()




    class Elimination:

        def __init__(self, fencers: list) -> None:

            self.sort_qualification()

            # Match information
            self.matches = {}
            self.first_round = True

            # Tree information
            self.round_counter = None

            
            # Calculate number of rounds
            self.round_counter = 0
            while len(fencers) > 1:
                fencers = fencers[::2]
                self.round_counter += 1


        def next_round(self):
            self.round_counter -= 1

        
        def round(self, custom = None) -> Literal["32th", "16th", "QF", "SF", "P3", "Final"]:
            counter = self.round_counter if custom == None else custom

            if counter == 5:
                return "32th"
            elif counter == 4:
                return "16th"
            elif counter == 3:
                return "QF"
            elif counter == 2:
                return "SF"
            elif counter == 0:
                return "P3"
            elif counter == 1:
                return "Final"
            else:
                return None



        def update_eliminated_fencers(self):
            if not self.first_round:
                if self.matches[self.round_counter + 1] != []:
                    for match in itertools.chain.from_iterable(self.matches[self.round_counter + 1]):
                        if match.winner != None:
                            self.eliminated_fencers.append(match.loser)


        def calc_wildcards(self, fencers: list) -> list:
            # if the number of fencers is not a power of 2, wildcards are needed
            if len(fencers) != 2**self.round_counter:
                # Calculate number of wildcards
                number_of_wildcards = 2**self.round_counter - len(fencers)

                print(f"Number of wildcards: {number_of_wildcards}")

                # Create wildcards
                for i in range(number_of_wildcards):
                    fencers.append(Wildcard(i))

            return fencers.copy()

        
        def create_first_round(self, fencers_to_assign: list):
            # Set up Wildcards
            fencers_to_assign = self.calc_wildcards(fencers_to_assign)
            
            # Clear fencers list
            self.fencers = []

            for _ in range((int(2**self.round_counter / 2))):
                self.matches[self.round_counter].append(EliminationMatch(fencers_to_assign[0], fencers_to_assign[-1], self.round()))
                self.fencers.append(fencers_to_assign[0])
                self.fencers.append(fencers_to_assign[-1])
                fencers_to_assign.pop(0)
                fencers_to_assign.pop(-1)


            self.first_round = False


        def create_finals(self, fencers_to_assign: list):
            for _ in range(int((2**self.round_counter) / 2)):
                # Create match lists for finals
                self.matches[1] = []
                self.matches[0] = []

                # Create Final match
                self.matches[1].append(EliminationMatch(fencers_to_assign[0], fencers_to_assign[1], self.round(), 1))

                # Create Bronze medal match
                self.matches[0].append(EliminationMatch(self.eliminated_fencers[-1], self.eliminated_fencers[-2], self.round(0), 1))


        def create_following_rounds(self, fencers_to_assign: list):
            for _ in range(int((2**self.round_counter) / 2)):
                # Create matches of the current round
                    self.matches[self.round_counter].append(EliminationMatch(fencers_to_assign[0], fencers_to_assign[1], self.round()))
                    fencers_to_assign.pop(0)
                    fencers_to_assign.pop(0)





        def create_matches(self):
            # Update eliminated fencers
            self.update_eliminated_fencers()

            # Create matches list for current round
            self.matches[self.round_counter] = []

            # Create a list of not eliminated fencers to assign to matches
            fencers_to_assign = [fencer for fencer in self.fencers if fencer not in self.eliminated_fencers]

            # If it is the first round, Wildcards are probably needed
            # Also, the fencers list must be updated (from standings of the group stage to the matches of the first round)
            if self.first_round:
                self.create_first_round(fencers_to_assign)
            
            elif self.round_counter == 1:
                self.create_finals(fencers_to_assign)

            else:
                self.create_following_rounds(fencers_to_assign)

        
        @property
        def round_description(self):
            if self.round_counter == 5:
                return "32th round"
            elif self.round_counter == 4:
                return "16th round"
            elif self.round_counter == 3:
                return "Quarterfinals"
            elif self.round_counter == 2:
                return "Semifinals"
            elif self.round_counter == 0:
                return "Bronze medal match"
            elif self.round_counter == 1:
                return "Final"
            else:
                return None