import math
import time
from fencer import *
from match import *
from piste import Piste

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
        fencers[i].prelim_group = counter
        grouping[counter - 1].append(fencers[i])
        counter += 1
        if counter > num_of_groups:
            counter = 1
    
    return grouping


# ------- Matchmaking Logic -------

def matchmaker_groups(fencers: list[Fencer], stage: Stage, prelim_round: int) -> list[Match]:
    # Create matchups
    matches = []

    # Every fencer fences against every other fencer
    for i in range(0, len(fencers)):
        for j in range(i + 1, len(fencers)):
            matches.append(GroupMatch(fencers[i], fencers[j], stage, prelim_round=prelim_round))

    return matches


def matchmaker_elimination(fencers: list, mode: Literal["ko", "repechage", "placement"], stage) -> list[Match]:
    # Create matchups
    matches = []

    if mode == "ko" or mode == "placement":
        for group in fencers:
            print([fencer.name for fencer in group])
            for i in range(int(len(group) / 2)):
                # Create match
                # The first fencer fences against the last fencer, the second fencer fences against the second last fencer, etc.
                matches.append(EliminationMatch(group[i], group[-i-1], stage=stage))
                # Assign Index
                group[i].elimination_value = i+1
                group[-i-1].elimination_value = i+1

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode

    return matches


# ------- Tournament Logic -------

def create_group_matches(fencers: List[List[Fencer]], stage: Stage, groups: int = None, prelim_round: int = None) -> list[Match]:
    # Create groups
    groups = assign_groups(fencers, groups)

    all_matches = []

    # Create matches
    for group in groups:
        group_matches = matchmaker_groups(group, stage, prelim_round=prelim_round)

        for match in group_matches:
            match.group = group[0].prelim_group
            all_matches.append(match)
    
    return all_matches


# ------- Sorting Algorithms -------

def sorting_fencers(fencers: list[Fencer]) -> list[Fencer]:
    # This method sorts fencers by overall score
    # sort by stage, win percentage, points difference, points for, points against
    fencers = sorted(fencers, key=lambda fencer: (fencer.final_rank, fencer.win_percentage(), fencer.points_difference_int(), fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"]), reverse=True)
    return fencers


def sort_matchups_in_preliminary_round(fencers: list[Fencer], matches: list[Match]) -> list[Match]:
    # The matches in the preliminary round are sorted in the most diverse way possible. Idealy, no fencer should have two matches back to back.
    # Initialize the dictionary of wait times
    wait_times = {}
    for fencer in fencers:
        if fencer.name not in wait_times:
            wait_times[fencer.name] = 0

    sorted_matches = []

    while matches != []:
        # Iterate over the matches
        for match in matches:
            # The match with the highest sum of wait time is chosen
            if wait_times[match.green.name] + wait_times[match.red.name] >= max([wait_times[fencer.name] for fencer in match]) + 1:
                # The match is removed from the list
                matches.remove(match)

                # The wait times of the fencers are reset
                wait_times[match.green.name] = -10
                wait_times[match.red.name] = -10

                # The match is added to the list of sorted matches
                sorted_matches.append(match)
            
            else:
                # The wait times of the fencers are updated
                wait_times[match.green.name] += 1
                wait_times[match.red.name] += 1

    for id in range(1, len(sorted_matches) + 1):
        sorted_matches[id - 1].sorting_id = id

    return sorted_matches


def next_tree_node(fencers_list: List[List[Fencer]], mode: Literal["ko", "repechage", "placement"] = "ko") -> list:

    transposed_list = []

    if mode == "ko" or mode == "placement":
        # Iterate over the sublists
        for sublist in fencers_list:      # in this for loop, the var sublist is a list of fencers

            advanced = []               # List to temporarily store the advanced fencers
            eliminated = []             # List to temporarily store the eliminated fencers

            # sort the sublist by elimination_value and who won
            # That means, that all we have now a list of fencers where each fencer with uneven index advances (0, 2, 4, ...), each fencer with even index is eliminated.
            sublist = sorted(sublist, key=lambda fencer: (fencer.elimination_value, fencer.last_match_won))
            
            print("\n\n\n")
            print([[fencer.elimination_value, fencer.last_match_won, fencer.name] for fencer in sublist])
            print("\n\n\n")

            # Iterate over the elements in the sublist
            for i in range(len(sublist)):
                
                # if the index of the fencer is even, the fencer is eliminated
                if i % 2 == 0:                      # if the index of the fencer is even
                    eliminated.append(sublist[i])   # Add the fencer to the eliminated list
                else:                               # else
                    advanced.append(sublist[i])     # Add the fencer to the advanced list

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

    # --- CONSTRUCTOR ---

    def __init__(
        self,
        id: str,
        name: str,
        fencers: list[Fencer],
        location: str,
        num_preliminary_rounds: str,
        num_preliminary_groups: str,
        first_elimination_round: str,
        elimination_mode: Literal["ko", "repechage", "placement"],
        number_of_pistes: str
        ):

        # Tournament information
        self.id = id
        self.name = name
        self.location = location

        # List of fencers in the tournament
        self.fencers = fencers

        # Custumizable tournament procedures
        self.num_preliminary_rounds = int(num_preliminary_rounds) if num_preliminary_rounds != "0" else None
        self.num_preliminary_groups = int(num_preliminary_groups) if num_preliminary_groups != "0" else None
        self.first_elimination_round = int(first_elimination_round) if first_elimination_round != "0" else None
        self.elimination_mode = elimination_mode
        self.only_elimination = True if self.num_preliminary_rounds == 0 else False

        # Pistes
        self.num_pistes: int = int(number_of_pistes)
        self.pistes: list[Piste] = []
        for i in range(self.num_pistes):
            self.pistes.append(Piste(i + 1))

        # --------------------

        # List of fencers in the preliminary round
        self.preliminary_fencers = []
        self.preliminary_matches = [list() for _ in range(self.num_preliminary_rounds)] # 2D list of Preliminary Rounds -> Matches

        # List of fencers in the elimination round
        self.elimination_fencers = [[]] # 2D list of Advanded Fencers / Eliminated Fencers for KO and Placement
        self.elimination_matches = []
        self.elimination_matches_archive = []

        # Stage of the tournament
        self.elimination_first_stage = Stage(math.ceil(math.log2(len(fencers)))) if self.first_elimination_round == None else Stage(math.log2(self.first_elimination_round))
        self.preliminary_stage = 1 if self.num_preliminary_rounds != None else None
        self.stage: Stage = Stage.PRELIMINARY_ROUND if not self.only_elimination else self.elimination_first_stage

        # Wildcards needed
        if len(self.fencers) > self.elimination_first_stage.value ** 2:
            self.num_wildcards = 0
        else:
            self.num_wildcards = 2 ** math.ceil(math.log2(len(self.fencers))) - len(self.fencers)

        # Create preliminary round
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.create_preliminary_round()
        else:
            self.create_next_elimination_round()


    # --- Creating Rounds ---

    def create_preliminary_round(self) -> None:
        # Create preliminary round
        self.preliminary_fencers = self.fencers
        self.preliminary_matches[self.preliminary_stage - 1] = create_group_matches(self.preliminary_fencers, self.stage, prelim_round=self.preliminary_stage - 1)
        self.preliminary_matches[self.preliminary_stage - 1] = sort_matchups_in_preliminary_round(self.preliminary_fencers ,self.preliminary_matches[self.preliminary_stage - 1])
        self.assign_pistes(self.preliminary_matches[self.preliminary_stage - 1])


    def create_next_elimination_round(self) -> None:
        # Create next (or first) elimination round

        # If it is the first elimination round, sort the fencers by overall score and append them to the elimination fencers list
        if self.elimination_matches == []:
            # Sort the fencers by overall score from Preliminary Round
            self.elimination_fencers = [sorting_fencers(self.fencers)]
            # If the first elimination round is customarily set, the list of fencers is cut to the length of the first elimination round
            if self.first_elimination_round != None:
                self.elimination_fencers = self.elimination_fencers[(self.first_elimination_round ** 2):]
            # Calculating Wildcards
            for i in range(0, self.num_wildcards) if self.num_wildcards != 0 else []:
                self.elimination_fencers[0].append(Wildcard(i+1))

        else:
            self.elimination_fencers = next_tree_node(self.elimination_fencers, self.elimination_mode)

        if self.elimination_matches != []: self.elimination_matches_archive.append(self.elimination_matches)
        self.elimination_matches = matchmaker_elimination(self.elimination_fencers, self.elimination_mode, self.stage)
        self.assign_pistes(self.elimination_matches)


    def assign_pistes(self, matches: list[Match]):
        for piste in self.pistes:
            if not piste.staged:
                for match in matches:
                    if match.piste == None and match.wildcard == False:
                        match.assign_piste(piste)
                        break


    def generate_matches(self) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.create_preliminary_round()

        else:
            raise NotImplementedError # TODO: Implement elimination round



    # --- GET Requests handling from client ---

    def get_standings(self) -> dict:
        # Get current standings and return them as a dictionary for the GUI
        standings = {
            "stage": self.stage.name.replace("_", " ") + f" {self.preliminary_stage}",
            "standings": [],
        }

        # Sort fencers by overall score
        fencers = sorting_fencers(self.fencers)

        for fencer in fencers:
            standings["standings"].append({
                "rank": fencers.index(fencer) + 1,
                "name": fencer.short_str,
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
                "stage": self.stage.name.replace("_", " ") + f" {self.preliminary_stage}",
                "matches": [],
            }
            for match in self.preliminary_matches[self.preliminary_stage - 1]:
                dictionary["matches"].append({
                    "id": match.id,
                    "group": match.group,
                    "piste": match.piste_str,
                    "green": match.green.short_str,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red.short_str,
                    "red_nationality": match.red.nationality,
                    "red_score": match.red_score,
                    "ongoing": match.match_ongoing,
                    "complete": match.match_completed
                })
            return dictionary

        else:
            dictionary = {
                "stage": self.stage.name,
                "matches": [],
            }
            for match in self.elimination_matches:
                dictionary["matches"].append({
                    "id": match.id,
                    "group": self.stage.name.replace("_", " ").title(),
                    "piste": match.piste_str,
                    "green": match.green.short_str,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red.short_str,
                    "red_nationality": match.red.nationality,
                    "red_score": match.red_score,
                    "ongoing": match.match_ongoing,
                    "complete": match.match_completed
                })
            print(dictionary)
            return dictionary


    def get_matches_left(self) -> str:
        if self.stage == Stage.PRELIMINARY_ROUND:
            return str(len([match for match in self.preliminary_matches[self.preliminary_stage - 1] if not match.match_completed]))
        else:
            return str(len([match for match in self.elimination_matches if not match.match_completed]))

    
    def get_dashboard_infos(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "stage": self.stage.name.replace("_", " ").replace("Top ", "").title() + (f" {self.preliminary_stage}" if self.stage == Stage.PRELIMINARY_ROUND else ""),
            "num_fencers": len(self.fencers),
            "num_clubs": len(set([fencer.club for fencer in self.fencers])),
            "num_prelim_groups": self.num_preliminary_groups if self.num_preliminary_groups != None else len(set([match.group for match in self.preliminary_matches[0]])),
            "num_prelim_rounds": self.num_preliminary_rounds,
            "elimination_mode": self.elimination_mode.upper(),
            "first_elimination_round": self.elimination_first_stage.name.replace("_", " ").title(),
            "num_wildcards": self.num_wildcards,
            "num_pistes": len(self.pistes),
            "num_matches": len(self.preliminary_matches[self.preliminary_stage - 1]) if self.stage == Stage.PRELIMINARY_ROUND else len(self.elimination_matches), # TODO Implement calculation for all matches
            "num_matches_completed": len([match for match in self.preliminary_matches[self.preliminary_stage - 1] if match.match_completed]) if self.stage == Stage.PRELIMINARY_ROUND else len([match for match in self.elimination_matches if match.match_completed]), # TODO Implement calculation for all matches
        }


    # --- POST Request handling from client ---

    def push_score(self, match_id: int, green_score: int, red_score: int) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            for group in (self.preliminary_matches):
                for match in group:
                    if match.id == match_id:
                        match.input_results(green_score, red_score)
            self.assign_pistes(self.preliminary_matches[self.preliminary_stage - 1])
                        
        else:
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.input_results(green_score, red_score)
            self.assign_pistes(self.elimination_matches)


    def set_active(self, match_id: int) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.assign_pistes(self.preliminary_matches[self.preliminary_stage - 1])
            for match in self.preliminary_matches[self.preliminary_stage - 1]:
                if match.id == match_id:
                    match.set_active()

        else:
            self.assign_pistes(self.elimination_matches)
            for match in self.elimination_matches:
                if match.id == match_id:
                    match.set_active()


    def next_stage(self) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.preliminary_stage += 1
            if self.preliminary_stage > self.num_preliminary_rounds:
                self.stage = self.elimination_first_stage
                self.create_next_elimination_round()
            else:
                self.create_preliminary_round()
        else:
            print(self.stage.value, self.stage.name)
            self.stage = self.stage.next_stage()
            print(self.stage.value, self.stage.name)
            self.create_next_elimination_round()


    # --- MISCELLANEOUS ---

    def simulate_current(self) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            length = len(self.preliminary_matches[self.preliminary_stage - 1])
            for match in self.preliminary_matches[self.preliminary_stage - 1]:
                # Set match active
                self.set_active(match.id)
                time.sleep(0.01)
                if random.choice([True, False]) is True:
                    self.push_score(match.id, 15, random.randint(0, 14))
                else:
                    self.push_score(match.id, random.randint(0, 14), 15)

                # Print status bar
                progress = round(self.preliminary_matches[self.preliminary_stage - 1].index(match) / length * 20)
                print(f"Simulating... |{'#' * progress}{' ' * (20 - progress)}|", end="\r")

            print(f"Simulating... |{'#' * 20}|")
            print("Simulation Done.")


        else:
            length = len(self.elimination_matches)
            for match in self.elimination_matches:
                self.set_active(match.id)
                if match.wildcard is True:
                    continue
                if random.choice([True, False]) is True:
                    self.push_score(match.id, 15, random.randint(0, 14))
                else:
                    self.push_score(match.id, random.randint(0, 14), 15)
                
                # Print status bar
                progress = round(self.elimination_matches.index(match) / length * 20)
                print(f"Simulating... |{'#' * progress}{' ' * (20 - progress)}|", end="\r")

            print(f"Simulating... |{'#' * 20}|")
            print("Simulation Done.")