import csv
import datetime
import math
import os
import random
import time
from typing import List, Tuple, Literal

from fuzzywuzzy import fuzz

import random_generator
from fencer import Fencer, Stage, Wildcard
from match import EliminationMatch, GroupMatch, Match
from piste import Piste
from exceptions import *
import logging

# -------| Logging |-------
try: # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('tournament')
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


# -------| Groups |-------

def assign_groups(fencers: List[Fencer], groups: int = None) -> List[List[Fencer]]:

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

    else:
        num_of_groups = groups

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


# -------| Matchmaking Logic |-------

def matchmaker_groups(fencers: List[Fencer], stage: Stage, prelim_round: int) -> List[Match]:
    # Create matchups
    matches = []

    # Every fencer fences against every other fencer
    for i in range(0, len(fencers)):
        for j in range(i + 1, len(fencers)):
            # Randomize the color of the fencers
            if type(fencers[i]) != "Wildcard" and type(fencers[j]) != "Wildcard":
                red = fencers[i] if random.randint(0, 1) == 0 else fencers[j]
                green = fencers[j] if red == fencers[i] else fencers[i]
            # Create match
            matches.append(GroupMatch(green, red, stage, prelim_round=prelim_round))

    return matches


def matchmaker_elimination(fencers: list, mode: Literal["ko", "repechage", "placement"], stage) -> List[Match]:
    # Create matchups
    matches = []

    if mode == "ko" or mode == "placement":
        for group in fencers:
            for i in range(int(len(group) / 2)):
                # Create match
                # The first fencer fences against the last fencer, the second fencer fences against the second last fencer, etc.
                if type(group[i]) == Wildcard and type(group[-i-1]) == Wildcard:
                    # If both fencers are wildcards, skip this match
                    continue
                
                # Randomize the color of the fencers
                red = group[i] if random.randint(0, 1) == 0 else group[-i-1]
                green = group[-i-1] if red == group[i] else group[i]
                matches.append(EliminationMatch(green, red, stage=stage if group[i].eliminated == False else Stage.PLACEMENTS))
                # Assign Index
                group[i].elimination_value = i+1
                group[-i-1].elimination_value = i+1

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode

    return matches


# -------| Tournament Logic |-------

def create_group_matches(fencers: List[List[Fencer]], stage: Stage, groups: int = None, prelim_round: int = None) -> List[Match]:
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


# -------| Sorting Algorithms |-------

def sorting_fencers(fencers: List[Fencer]) -> List[Fencer]:
    # This method sorts fencers by overall score
    # sort by stage, win percentage, points difference, points for, points against
    fencers = sorted(fencers, key=lambda fencer: (-(fencer.disqualified), -(fencer.final_rank if fencer.final_rank != None else float('0')), fencer.win_percentage(), fencer.points_difference_int(), fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"]), reverse=True)
    return fencers


def sort_matchups_in_preliminary_round(fencers: List[Fencer], matches: List[Match]) -> List[Match]:
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


def next_tree_node(fencers_list: List[List[Fencer]], stage, mode: Literal["ko", "repechage", "placement"] = "ko", final: bool = False) -> list:

    transposed_list = []

    if mode == "ko" or mode == "placement":
        # Iterate over the sublists
        for sublist in fencers_list:      # in this for loop, the var sublist is a list of fencers

            advanced = []               # List to temporarily store the advanced fencers
            eliminated = []             # List to temporarily store the eliminated fencers

            # sort the sublist by elimination_value and who won
            # That means, that all we have now a list of fencers where each fencer with uneven index advances (1, 3, 5, ...), each fencer with even index is eliminated.
            sublist = sorted(sublist, key=lambda fencer: (fencer.elimination_value if fencer.elimination_value else float('inf'), fencer.last_match_won if fencer.last_match_won else False)) # TODO check if this works (float('inf')

            # Iterate over the elements in the sublist
            for i in range(len(sublist)):
                
                # if the index of the fencer is even, the fencer is eliminated
                if i % 2 == 0:                      # if the index of the fencer is even
                    eliminated.append(sublist[i])   # Add the fencer to the eliminated list
                else:                               # else
                    advanced.append(sublist[i])     # Add the fencer to the advanced list

            # Add the advanced and eliminated lists to the transposed list in the correct order (advanced first, then eliminated)
            transposed_list.append(advanced)
            for fencer in eliminated:
                fencer.eliminated = True
                if mode == "ko":
                    fencer.final_rank = stage

            if mode == "placement":
                # Remove Wildcards from the eliminated list to sort all eliminated fencers by elimination_value
                wildcards = []
                for fencer in eliminated:
                    if type(fencer) == Wildcard:
                        wildcards.append(fencer)
                        eliminated.remove(fencer)
                # Sort the eliminated list by elimination_value and append Wildcards
                eliminated = sorted(eliminated, key=lambda fencer: fencer.elimination_value, reverse=True)
                eliminated += wildcards
                transposed_list.append(eliminated) # If the mode is ko, the eliminated list is not added to the transposed list. All losers are eliminated.
                for fencer in eliminated:
                    fencer.eliminated = True

            else:
                if final:
                    transposed_list.append(eliminated)

                for fencer in eliminated:
                    fencer.final_rank = stage + 4
                    fencer.eliminated = True
                for fencer in advanced:
                    fencer.final_rank = stage - 1 + 4
    

    elif mode == "repechage":
        raise NotImplementedError("Repechage mode not implemented yet") # TODO implement repechage mode      

    else:
        raise ValueError("Mode not supported")

    # Return the transposed list
    return transposed_list
    

def save_final_ranking(fencers_list: List[List[Fencer]], mode: Literal["ko", "placement", "repechage"]) -> list:
    num_fencers = len(fencers_list)

    for i in range(num_fencers):
        fencer_1 = fencers_list[i][0]
        fencer_2 = fencers_list[i][1]

        if fencer_1.last_match_won:
            fencer_1.final_rank = i * 2 + 1
            fencer_2.final_rank = i * 2 + 2
        else:
            fencer_1.final_rank = i * 2 + 2
            fencer_2.final_rank = i * 2 + 1

        if mode == "ko" and i == 1:
            break


# -------| Approval procedure and logging |-------

def register_approval(fencer_id, fencer_name, tournamnet_id, timestamp, round, group, device_id):
    # Check if folder /approvals exists
    if not os.path.exists("approvals"):
        os.mkdir("approvals")
    # Check if approval file for tournament exists
    if not os.path.exists(f"approvals/{tournamnet_id}.csv"):
        with open(f"approvals/{tournamnet_id}.csv", "w") as file:
            csv.writer(file).writerow(["device_id", "fencer_id", "fencer_name", "timestamp", "round", "group"])
    # Add fencer to approval file
    with open(f"approvals/{tournamnet_id}.csv", "r") as file:
        approvals = list(csv.reader(file))
    with open(f"approvals/{tournamnet_id}.csv", "a") as file:
        csv.writer(file).writerow([device_id, fencer_id, fencer_name, timestamp, round, group])
    return True


# -------| Tournament Base Class |-------

class Tournament:

    # ---| CONSTRUCTOR |---

    def __init__(
        self,
        id: str,
        name: str,
        location: str,
        master_email: str,
        password: str,
    
        fencers: List[Fencer],
    
        num_preliminary_rounds: str,
        num_preliminary_groups: str,
        first_elimination_round: str,
        elimination_mode: Literal["ko", "repechage", "placement"],
    
        number_of_pistes: str,

        allow_fencers_to_start_matches = False,
        allow_fencers_to_input_scores = False,
        allow_fencers_to_referee = False,

        simulation_active: bool = False,
        ):

        # Tournament information
        self.created_at = datetime.datetime.now()
        self.id = id
        self.password = password
        self.master_email = master_email
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

        # Permissions / Rights of the fencers
        self.allow_fencers_to_start_matches = allow_fencers_to_start_matches
        self.allow_fencers_to_input_scores = allow_fencers_to_input_scores
        self.allow_fencers_to_referee = allow_fencers_to_referee

        # Advanced Configuration
        self.simulation_active = simulation_active
        


        # --------------------

        # Pistes
        self.num_pistes: int = int(number_of_pistes)
        self.pistes: List[Piste] = []
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

        # Elimination Bracket(s)
        self.elimination_brackets: List[self.Bracket] = []

        # Stage of the tournament
        self.elimination_first_stage = Stage(math.ceil(math.log2(len(fencers)))) if self.first_elimination_round == None else Stage(math.log2(self.first_elimination_round))
        self.preliminary_stage = 1 if self.num_preliminary_rounds != None else None
        self.stage: Stage = Stage.PRELIMINARY_ROUND if not self.only_elimination else self.elimination_first_stage

        # Wildcards needed
        if len(self.fencers) > 2 ** self.elimination_first_stage.value:
            self.num_wildcards = 0
        else:
            self.num_wildcards = 2 ** math.ceil(math.log2(len(self.fencers))) - len(self.fencers)

        print("Number of wildcards: ", self.num_wildcards)

        # Create preliminary round
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.create_preliminary_round()
        else:
            self.create_next_elimination_round()

        # --------------------
        # Cookies
        self.master_cookies = [] 
        self.referee_cookies = [] 

        # --------------------
        # Logging
        logger.info(f"Created tournament {self.name} ({self.id}) with {len(self.fencers)} fencers")
        logger.debug(f"Simulation is {'active' if self.simulation_active else 'inactive'}")

    
    # ---| Properties |---
    
    @property
    def matches_of_current_preliminary_round(self) -> List[Match]:
        return self.preliminary_matches[self.preliminary_stage - 1]
    
    @property
    def matches_of_current_elimination_round(self) -> List[Match]:
        if self.stage == Stage.PRELIMINARY_ROUND:
            return []
        return [matches for matches in self.elimination_matches if matches.stage == self.stage]

    @property
    def all_matches(self) -> List[Match]:
        matches = []
        for round in self.preliminary_matches:
            matches.extend(round)
        matches.extend(self.elimination_matches)

        return matches


    # ---| Misc |---
    def get_fencer_rank(self, fencer_id: str) -> int:
        fencers = sorting_fencers(self.fencers)
        for i, fencer in enumerate(fencers):
            if fencer.id == fencer_id:
                return i + 1


    # --- Creating Rounds ---

    def create_preliminary_round(self) -> None:
        # Create preliminary round
        self.preliminary_fencers = self.fencers
        self.preliminary_matches[self.preliminary_stage - 1] = create_group_matches(self.preliminary_fencers, self.stage, groups=self.num_preliminary_groups, prelim_round=self.preliminary_stage - 1)
        self.preliminary_matches[self.preliminary_stage - 1] = sort_matchups_in_preliminary_round(self.preliminary_fencers , self.matches_of_current_preliminary_round)
        self.assign_pistes()


    def create_next_elimination_round(self, final: bool = False) -> None:
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
            self.elimination_fencers = next_tree_node(self.elimination_fencers, self.stage.value, self.elimination_mode, final = final)

        if self.elimination_matches != []: self.elimination_matches_archive.append(self.elimination_matches)
        self.elimination_matches = matchmaker_elimination(self.elimination_fencers, self.elimination_mode, self.stage)
        self.assign_pistes()

        for fencer in self.fencers:
            fencer.stage = self.stage


    def assign_pistes(self):
        logger.debug("Piste assignment")
        matches = sorted(self.all_matches, key=lambda match: match.priority, reverse=True)
        for match in matches:
            if (
                match.piste == None
                and
                match.match_completed == False
                and
                match.wildcard_or_disq == False
                and

                not (
                    match.green.is_staged
                    or
                    match.red.is_staged
                )

                and

                not (
                    match.green.in_match
                    and
                    match.red.in_match
                )
            ):
                for piste in sorted(self.pistes, key=lambda piste: piste.occupied):
                    if not piste.staged and not piste.disabled:
                        match.assign_piste(piste)
                        break
                else:
                    # break
                    pass


    def generate_matches(self) -> None:
        if self.stage == Stage.PRELIMINARY_ROUND:
            self.create_preliminary_round()

        else:
            raise NotImplementedError # TODO: Implement elimination round



    # --- GET Requests handling from client ---

    def get_standings(self, group, gender=None, handedness=None, age_group=None) -> dict:
        # Get current standings and return them as a dictionary for the GUI
        standings = {
            "stage": str(self.stage),
            "first_elimination_round": self.first_elimination_round,
            "standings": [],
        }

        # Sort fencers by overall score
        fencers = sorting_fencers(self.fencers)


        if not group:
            group = "all"

        # If a specific group is requested, only return the fencers of that group
        if group != "all" and self.stage == Stage.PRELIMINARY_ROUND:
            filtered_fencers = []
            for fencer in fencers:
                if fencer.prelim_group == int(group):
                    filtered_fencers.append(fencer)
            fencers = filtered_fencers
        
        if gender != None:
            filtered_fencers = []
            for fencer in fencers:
                if fencer.gender == gender:
                    filtered_fencers.append(fencer)
            fencers = filtered_fencers

        if handedness != None:
            filtered_fencers = []
            for fencer in fencers:
                if fencer.handedness == handedness:
                    filtered_fencers.append(fencer)
            fencers = filtered_fencers
        
        if age_group != None:
            filtered_fencers = []
            age_range = age_group.split("-")
            for fencer in fencers:
                if int(fencer.age) >= int(age_range[0]) and int(fencer.age) <= int(age_range[1]):
                    filtered_fencers.append(fencer)
            fencers = filtered_fencers


        for fencer in fencers:
            standings["standings"].append({
                "rank": fencers.index(fencer) + 1,
                "id": fencer.id,
                "name": fencer.short_str,
                "club": fencer.club,
                "nationality": fencer.nationality,
                "gender": fencer.gender,
                "age": fencer.age,
                "handedness": fencer.handedness,
                "win_percentage": fencer.win_percentage(),
                "win_lose": f"{fencer.statistics['overall']['wins']} - {fencer.statistics['overall']['losses']}",
                "points_difference": fencer.points_difference(),
                "points_for": fencer.statistics["overall"]["points_for"],
                "points_against": fencer.statistics["overall"]["points_against"],
                "eliminated": fencer.eliminated,
            })

        return standings


    def get_matches(self) -> dict:
        if self.stage == Stage.PRELIMINARY_ROUND:
            dictionary = {
                "stage": self.stage.name.replace("_", " ") + f" {self.preliminary_stage}",
                "matches": [],
            }
            for match in self.matches_of_current_preliminary_round:
                dictionary["matches"].append({
                    "id": match.id,
                    "group": match.group,
                    "piste": match.piste_str,
                    "green": match.green.short_str,
                    "green_id": match.green.id,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red.short_str,
                    "red_id": match.red.id,
                    "red_nationality": match.red.nationality,
                    "red_score": match.red_score,
                    "ongoing": match.match_ongoing,
                    "complete": match.match_completed,
                    "piste_occupied": match.piste.occupied if match.piste else None,
                    "priority": match.priority,
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
                    "group": match.stage.name.replace("_", " ").title(),
                    "piste": match.piste_str,
                    "green": match.green.short_str,
                    "green_id": match.green.id,
                    "green_nationality": match.green.nationality,
                    "green_score": match.green_score,
                    "red": match.red.short_str,
                    "red_id": match.red.id,
                    "red_nationality": match.red.nationality,
                    "red_score": match.red_score,
                    "ongoing": match.match_ongoing,
                    "complete": match.match_completed,
                    "piste_occupied": match.piste.occupied if match.piste else None,
                    "priority": match.priority,
                })
            return dictionary


    def get_matches_left(self) -> str:
        if self.stage == Stage.PRELIMINARY_ROUND:
            return str(len([match for match in self.matches_of_current_preliminary_round if not match.match_completed]))
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
            "num_nationalities": len(set([fencer.nationality for fencer in self.fencers])),
            "num_prelim_groups": self.num_preliminary_groups if self.num_preliminary_groups != None else len(set([match.group for match in self.preliminary_matches[0]])),
            "num_prelim_rounds": self.num_preliminary_rounds,
            "elimination_mode": self.elimination_mode.upper(),
            "first_elimination_round": self.elimination_first_stage.name.replace("_", " ").title(),
            "num_wildcards": self.num_wildcards,
            "num_pistes": len(self.pistes),
            "num_matches": len(self.matches_of_current_preliminary_round) if self.stage == Stage.PRELIMINARY_ROUND else len(self.elimination_matches), # TODO Implement calculation for all matches
            "num_matches_completed": len([match for match in self.matches_of_current_preliminary_round if match.match_completed]) if self.stage == Stage.PRELIMINARY_ROUND else len([match for match in self.elimination_matches if match.match_completed]), # TODO Implement calculation for all matches
            "simulation_active": self.simulation_active,
        }
    
    def get_piste_status(self, requested_piste: int) -> list:
        if requested_piste != None:
            piste_list = [self.pistes[requested_piste - 1]]
        else:
            piste_list = self.pistes
        
        piste_status = []
        for piste in piste_list:
            match_on_piste = None

            if piste.disabled:
                match_on_piste = None

            elif piste.occupied:
                for match in self.all_matches:
                    if match.piste == piste and match.match_ongoing:
                        match_on_piste = match
                        break

            elif piste.staged:
                for match in self.all_matches:
                    if match.piste == piste and not match.match_completed and not match.match_ongoing:
                        match_on_piste = match
                        break
            
            piste_status.append({
                "status": piste.status,
                "match_id": match_on_piste.id if piste.staged and not piste.disabled else None,
                "green": match_on_piste.green.short_str if match_on_piste else None,
                "green_id": match_on_piste.green.id if match_on_piste else None,
                "red": match_on_piste.red.short_str if match_on_piste else None,
                "red_id": match_on_piste.red.id if match_on_piste else None,
            })

        return piste_status if requested_piste == None else piste_status[0]

    def toggle_piste(self, piste: int) -> None:
        if self.pistes[piste - 1].occupied:
            raise OccupiedPisteError("Piste is occupied and cannot be disabled. Clear the piste first.")
        elif self.pistes[piste - 1].disabled:
            self.pistes[piste - 1].disabled = False
            print(f"Piste {piste} enabled.")
        else:
            for match in self.all_matches:
                if (
                    match.piste == self.pistes[piste - 1]
                    and
                    not match.match_completed
                ):
                    match.piste = None
                    match.green.is_staged = False
                    match.red.is_staged = False
            self.pistes[piste - 1].disable()
                


        self.assign_pistes()

    def get_fencer_object(self, fencer_id: int) -> Fencer:
        for fencer in self.fencers:
            if fencer.id == fencer_id:
                return fencer
        return None

    def get_current_rank(self, fencer: Fencer) -> int:
        return sorting_fencers(self.fencers).index(fencer) + 1

    def get_current_group_rank(self, fencer: Fencer) -> int:
        group = []
        for rank in sorting_fencers(self.fencers):
            if fencer.prelim_group == rank.prelim_group:
                group.append(rank)
        return group.index(fencer) + 1
                

    def get_opponent(self, fencer: Fencer, match: Match) -> dict:
        if match.green == fencer:
            opponent = "red"
        elif match.red == fencer:
            opponent = "green"

        return {
            "id": match[opponent].id,
            "name": match[opponent].short_str,
            "club": match[opponent].club,
            "nationality": match[opponent].nationality,
            "last_matches": match[opponent].last_matches,
            "current_rank": self.get_current_rank(match[opponent]),
            "current_group_rank": self.get_current_group_rank(match[opponent]) if self.stage == Stage.PRELIMINARY_ROUND else None,
        }

    def get_fencer_hub_information(self, fencer_id: int) -> dict:
        fencer = self.get_fencer_object(fencer_id)
        if fencer:
            next_matches = []
            for match in self.matches_of_current_preliminary_round if self.stage == Stage.PRELIMINARY_ROUND else self.elimination_matches:
                if (match.green == fencer or match.red == fencer) and not match.match_completed:
                    next_matches.append({
                        "id": match.id,
                        "piste": match.piste_str,
                        "piste_occupied": match.piste.occupied if match.piste else None,
                        "color": "green" if match.green == fencer else "red",
                        "ongoing": match.match_ongoing,
                        "opponent": self.get_opponent(fencer, match),
                    })

            return {
                "id": fencer.id,
                "name": fencer.short_str,
                "club": fencer.club,
                "nationality": fencer.nationality,
                "start_number": fencer.start_number,
                "allow_fencers_to_start_matches": self.allow_fencers_to_start_matches,
                "allow_fencers_to_input_scores": self.allow_fencers_to_input_scores,
                "allow_fencers_to_referee": self.allow_fencers_to_referee,
                "gender": fencer.gender if fencer.gender else "–",
                "age": fencer.age if fencer.age else "–",
                "handedness": fencer.handedness if fencer.handedness else "–",
                "approved_tableau": fencer.approved_tableau,
                "next_matches": next_matches,
                "outcome_last_matches": fencer.outcome_last_matches,
                "last_matches": fencer.last_matches,
                "current_rank": self.get_current_rank(fencer),
                "group": fencer.prelim_group if self.stage == Stage.PRELIMINARY_ROUND else None,
                "current_group_rank": self.get_current_group_rank(fencer) if self.stage == Stage.PRELIMINARY_ROUND else None,
                "group_stage": True if self.stage == Stage.PRELIMINARY_ROUND else False,
                "statistics": fencer.statistics,
                "win_percentage": fencer.win_percentage(),
                "points_difference": fencer.points_difference(),
                "points_per_match": fencer.points_per_game(),
                "graph_data": {
                    "standings": {
                        "labels": fencer.game_lables,
                        "data": fencer.standings_history,
                        "y_max": len(self.fencers),
                    },
                    "points_difference": {
                        "labels": fencer.game_lables,
                        "data": fencer.difference_history
                    },
                    "points_difference_per_match": {
                        "data": fencer.difference_per_match_history
                    },
                },
            }   


    # --- POST Request handling from client ---

    def push_score(self, match_id: int, green_score: int, red_score: int) -> None:
        for match in self.all_matches:
            if match.id == match_id:
                if match.match_completed:
                    self.correct_score(match, green_score, red_score)
                else:
                    match.input_results(green_score, red_score)
                    green_rank = self.get_fencer_rank(match.green.id)
                    red_rank = self.get_fencer_rank(match.red.id)
                    match.green.update_rank(green_rank)
                    match.red.update_rank(red_rank)

        self.assign_pistes()

    
    def correct_score(self, match: int, green_score: int, red_score: int) -> None:
        green_fencer = match.green
        old_green_score = match.green_score
        red_fencer = match.red
        old_red_score = match.red_score
        match.input_results(green_score, red_score, skip_update_statistics=True)

        green_fencer.correct_statistics(match, red_fencer, old_green_score, old_red_score, green_score, red_score, match.prelim_round if self.stage == Stage.PRELIMINARY_ROUND else 0)
        red_fencer.correct_statistics(match, green_fencer, old_red_score, old_green_score, red_score, green_score, match.prelim_round if self.stage == Stage.PRELIMINARY_ROUND else 0)


    def set_active(self, match_id: int, override_flag=False) -> None:
        for match in self.all_matches:
            if match.id == match_id:
                # If there is a match on the same piste, the piste staged status is not set to False
                for match2 in self.all_matches:
                    if match2.piste == match.piste and match2.match_ongoing:
                        if not override_flag:
                            raise OccupiedPisteError("Piste " + str(match.piste.number) + " is already occupied by match " + match2.id)
                        match.set_active(staged=True)
                        break
                else:
                    match.set_active()

        self.assign_pistes()


    def prioritize_match(self, match_id, value) -> None:
        for match in (self.matches_of_current_preliminary_round if self.stage == Stage.PRELIMINARY_ROUND else self.elimination_matches):
            if match.id == match_id:
                match.priority = value
                print("match " + match.id + " priority set to ", match.priority)

    
    def assign_certain_piste(self, match_id, piste: int) -> None:
        match = self.get_match_by_id(match_id)
        requested_piste = self.pistes[piste - 1]
        old_piste = match.piste

        # If the requested piste is disabled, the match is not assigned to it
        if requested_piste.disabled:
            raise PisteError("Piste " + str(piste) + " is disabled.")

        # There are 4 cases:

        if old_piste != None:
            if old_piste.staged and not requested_piste.staged:
                # 1. The match is already staged, and there is no other match staged on the requested piste
                #   -> The staged status of the other piste is set to false
                print("Case 1")
                old_piste.staged = False

            elif old_piste.staged and requested_piste.staged:
                # 2. The match is already staged, and there is another match staged on the same piste
                #   -> The matches switch piste and the staged status remains true for both
                print("Case 2")
                for match2 in self.all_matches:
                    if match2.piste == requested_piste and match2.match_ongoing == False and match2.match_completed == False:
                        match2.assign_piste(old_piste)
                        break

            else:
                raise Exception("Error in assign_certain_piste: match.piste != None, but old_piste.staged and requested_piste.staged are both false. This should not happen.")

        else:
            if not requested_piste.staged:
                # 3. The match is not staged, and there is no other match staged on the same piste
                #   -> The match is staged on the requested piste
                print("Case 3")

            else:
                # 4. The match is not staged, but there is another match staged on the same piste
                #   -> The match is staged on the requested piste, the piste assignment for the other piste is removed
                print("Case 4")
                for match2 in self.all_matches:
                    if match2.piste == requested_piste and match2.match_ongoing == False and match2.match_completed == False:
                        match2.piste = None
                        break

        # In all cases, the match is staged on the requested piste
        match.assign_piste(requested_piste)

        self.assign_pistes()

    def remove_piste_assignment(self, match_id) -> None:
        match = self.get_match_by_id(match_id)
        if match.piste != None:
            match.piste.staged = False
            match.piste = None
            match.green.is_staged = False
            match.red.is_staged = False
        else:
            raise PisteError("Error in remove_piste_assignment: The match is not staged on a piste and therefore cannot be removed from a piste.")



    def next_stage(self) -> None:

        for piste in self.pistes:
            piste.reset()

        self.export_stage_results()

        if self.stage == Stage.PRELIMINARY_ROUND:
            self.preliminary_stage += 1
            if self.preliminary_stage > self.num_preliminary_rounds:
                self.stage = self.elimination_first_stage
                self.create_next_elimination_round()
                self.elimination_brackets.append(self.Bracket(self.matches_of_current_elimination_round, self.stage, "Elimination Bracket"))  # TODO implement looser bracket

            else:
                self.create_preliminary_round()

        elif self.stage == Stage.SEMI_FINALS:
            self.stage = Stage.GRAND_FINAL
            self.create_next_elimination_round(final = True)
            self.elimination_brackets[0].create_new_round(self.matches_of_current_elimination_round, self.stage)
        
        elif self.stage == Stage.GRAND_FINAL:
            self.stage = Stage.FINISHED

            save_final_ranking(self.elimination_fencers, self.elimination_mode)
            self.export_final_ranking()


        elif self.stage == Stage.FINISHED:
            raise StageError("Error in next_stage: The tournament is already finished.")

        else:
            self.stage = self.stage.next_stage()
            self.create_next_elimination_round()
            self.elimination_brackets[0].create_new_round(self.matches_of_current_elimination_round, self.stage)

        for fencer in self.fencers:
            fencer.approved_tableau = False

        logger.info(f"Stage advanced to {self.stage.name}.")

    
    # ---| Search |---
    def get_fencer_by_id(self, fencer_id) -> Fencer:
        for fencer in self.fencers:
            if fencer.id == fencer_id:
                return fencer
        raise SearchError(f"Fencer with id {fencer_id} not found.")
    
    def get_fencer_id_by_name(self, fencer_name) -> str:
        return self.get_fencer_by_name(fencer_name).id
    
    def get_fencer_by_name(self, fencer_name) -> Fencer:
        best_match = None
        best_ratio = 0
        for fencer in self.fencers:
            ratio = fuzz.token_set_ratio(fencer.name, fencer_name)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = fencer
        if best_ratio >= 70: # to be adjusted according to the desired threshold
            return best_match
        raise SearchError(f"Could not match requested fencer name {fencer_name} to any fencer in the tournament.")
    
    def get_fencer_id_by_start_number(self, start_number) -> str:
        return self.get_fencer_by_start_number(start_number).id
    
    def get_fencer_by_start_number(self, start_number) -> Fencer:
        if start_number < len(self.fencers):
            for fencer in self.fencers:
                if fencer.start_number == int(start_number):
                    return fencer
        raise SearchError(
            f"Could not match requested start number {start_number} to any fencer in the tournament.")

    def get_match_by_id(self, match_id) -> Match:
        for match in self.all_matches:
            if match.id == match_id:
                return match
        raise SearchError(f"Match with id {match_id} not found.")

    def get_tableau_array(self, group) -> list:
        tableau = []

        fencers_in_group = []
        for fencer in self.fencers:
            if fencer.prelim_group == int(group):
                fencers_in_group.append(fencer)
        
        fencers_in_group = sorting_fencers(fencers_in_group)

        # For the first row of the tableau, all fencers get a column, the first column is empty
        tableau.append([])
        tableau[0].append({"cell_type": "blank_header"})
        for fencer in fencers_in_group:
            tableau[0].append({
                "cell_type": "header",
                "id": fencer.id,
                "name": fencer.short_str,
                "nationality": fencer.nationality,
                "approved": fencer.approved_tableau
            })

        # From now on, the first column is the fencer's name, the other columns are the results against the fencer in the first row
        # flip_score = True
        for fencer in fencers_in_group:
            tableau.append([])
            tableau[-1].append({
                "cell_type": "header",
                "id": fencer.id,
                "name": fencer.short_str,
                "nationality": fencer.nationality,
                "approved": fencer.approved_tableau
            })

            for opponent in fencers_in_group:
                if fencer.id == opponent.id:
                    tableau[-1].append({
                        "cell_type": "blank"
                    })
                
                else:
                    # Search all matches of the match
                    for match in self.matches_of_current_preliminary_round:
                        if match.green.id == fencer.id and match.red.id == opponent.id:
                            tableau[-1].append({
                                "cell_type": "result",
                                "match_id": match.id,
                                "finished": match.match_completed,
                                "content": match.green_score,
                                "win": True if match.red_score < match.green_score else False
                            })
                        elif match.green.id == opponent.id and match.red.id == fencer.id:
                            tableau[-1].append({
                                "cell_type": "result",
                                "match_id": match.id,
                                "finished": match.match_completed,
                                "content": match.red_score,
                                "win": True if match.green_score < match.red_score else False
                            })
        
        return tableau

    def get_winner(self):
        if self.stage != Stage.FINISHED:
            raise SystemError("Tournament not finished yet.")
        return sorting_fencers(self.fencers)[0]


    def approve_tableau(self, round, group, timestamp, fencer_id, device_id):
        # TODO need to implement a check if all approvals are in before advancing to the next stage
        if self.stage == Stage.PRELIMINARY_ROUND:
            if self.preliminary_stage == int(round):
                for fencer in self.fencers:
                    if fencer.id == fencer_id:
                        if register_approval(fencer_id, fencer.short_str, self.id, timestamp, round, group, device_id) and fencer.approved_tableau == False:
                            fencer.approved_tableau = True
                            return {"success": True, "message": "Tableau approved"}
        return {"success": False, "message": "Tableau not approved"}


    def disqualify_fencer(self, fencer_id, reason = None):
        fencer = self.get_fencer_by_id(fencer_id)
        fencer.disqualify(reason)

        logger.info(f"Fencer {fencer} disqualified for '{reason if reason else 'No reason given'}'")

        # All unfinished matches of the fencer are automatically finished
        for match in self.all_matches:
            if match.match_completed == False:
                if match.green.id == fencer_id:
                    match.match_completed = True
                    match.red_score = 1
                    match.wildcard_or_disq = True
                    match.red.update_statistics_wildcard_or_disq_game(self, disq = True)
                elif match.red.id == fencer_id:
                    match.match_completed = True
                    match.green_score = 1
                    match.wildcard_or_disq = True
                    match.green.update_statistics_wildcard_or_disq_game(self, disq = True)


    def revoke_disqulification(self, fencer_id):
        fencer = self.get_fencer_by_id(fencer_id)
        fencer.revoke_disqualification()
        logger.info(f"Disqualification of fencer {fencer} revoked")
                
                    






    # --- General Information ---
    def get_num_groups(self) -> int:
        if self.stage == Stage.PRELIMINARY_ROUND:
            num_groups = 0
            for fencer in self.fencers:
                if fencer.prelim_group > num_groups:
                    num_groups = fencer.prelim_group
            return num_groups
        else:
            return 0


    # ---| Exporting |---

    def export_stage_results(self) -> list:

        # Check if the results folder exists, if not create it
        if not os.path.exists("results"):
            os.makedirs("results")

        # Check if the results folder for this tournament exists, if not create it
        if not os.path.exists(f"results/{self.id}"):
            os.makedirs(f"results/{self.id}")
        
        document_number = len(os.listdir(f"results/{self.id}")) + 1

        match_results = self.export_matches()

        if self.stage == Stage.PRELIMINARY_ROUND:
            tableaus = []
            for group in range(1, self.get_num_groups() + 1):
                tableaus.append(self.get_tableau_array(group))

        # Create a CSV file with the results
        with open(f"results/{self.id}/{document_number}-{self.id}-{str(self.stage).replace(' ', '_')}{('-' + str(self.preliminary_stage)) if self.stage == Stage.PRELIMINARY_ROUND else ''}.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",", quotechar=" ", quoting=csv.QUOTE_MINIMAL)
            
            # General Information
            csvwriter.writerow(["Tournament", self.name])
            csvwriter.writerow(["ID", self.id])
            csvwriter.writerow(["Stage", self.stage])
            if self.stage == Stage.PRELIMINARY_ROUND: csvwriter.writerow(["Preliminary Round", f"{self.preliminary_stage} of {self.num_preliminary_rounds}"])
            csvwriter.writerow([""])
            csvwriter.writerow([""])

            # Append Match Results
            csvwriter.writerow(["Results"])
            csvwriter.writerow(["Match ID", "Group", "Red", "Red Score", "Green Score", "Green", "Match Started", "Match Completed"])
            for match in match_results:
                csvwriter.writerow([match["id"], match["group"], match["red"], match["red_score"], match["green_score"], match["green"], match["match_started"], match["match_completed"]])
            
            # Append Tableaus                
            if self.stage == Stage.PRELIMINARY_ROUND: 
                csvwriter.writerow([""])
                csvwriter.writerow([""])
                csvwriter.writerow(["Tableau"])
                for tableau in tableaus:
                    csvwriter.writerow([f""])
                    temp_row = []
                    temp_row.append(f"Group {tableaus.index(tableau) + 1}") # The first cell of the header is empty
                    for row in tableau:
                        for cell in row:
                            if cell["cell_type"] == "header":
                                temp_row.append(cell["name"])
                            elif cell["cell_type"] == "blank":
                                temp_row.append("-")
                            elif cell["cell_type"] == "result":
                                temp_row.append(cell["content"])
                        csvwriter.writerow(temp_row)
                        temp_row = []
            
            # Append Ranking
            csvwriter.writerow([""])
            csvwriter.writerow([""])
            csvwriter.writerow(["Current Ranking"])
            csvwriter.writerow(["Rank", "Name", "Club", "Nationality", "W%", "W-L", "PD", "P+", "P-", "Gender", "Handedness", "Age", "Eliminated"])
            for fencer in sorting_fencers(self.fencers):
                csvwriter.writerow([self.get_current_rank(fencer), fencer.short_str, fencer.club, fencer.nationality, fencer.win_percentage(), f'{fencer.statistics["overall"]["wins"]}-{fencer.statistics["overall"]["losses"]}', fencer.statistics["overall"]["points_for"] - fencer.statistics["overall"]["points_against"], fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"], fencer.gender, fencer.handedness, fencer.age, fencer.eliminated])

            csvwriter.writerow([""])
            csvwriter.writerow([""])
            csvwriter.writerow([""])
            csvwriter.writerow(["Created:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])


    def export_final_ranking(self) -> list:
        document_number = len(os.listdir(f"results/{self.id}")) + 1

        if self.stage != Stage.FINISHED:
            raise Exception("Tournament is not finished yet")
        with open(f"results/{self.id}/{document_number}-{self.id}-FinalStandings.csv", "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",", quotechar=" ", quoting=csv.QUOTE_MINIMAL)
            
            # General Information
            csvwriter.writerow(["Tournament", self.name])
            csvwriter.writerow(["ID", self.id])
            csvwriter.writerow(["Final Standings"])
            csvwriter.writerow([""])
            csvwriter.writerow([""])

            csvwriter.writerow(["Rank", "Name", "Club", "Nationality", "W%", "W-L", "PD", "P+", "P-", "Gender", "Handedness", "Age", "Eliminated"])
            for fencer in sorting_fencers(self.fencers):
                csvwriter.writerow([self.get_current_rank(fencer), fencer.short_str, fencer.club, fencer.nationality, fencer.win_percentage(), f'{fencer.statistics["overall"]["wins"]}-{fencer.statistics["overall"]["losses"]}', fencer.statistics["overall"]["points_for"] - fencer.statistics["overall"]["points_against"], fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"], fencer.gender, fencer.handedness, fencer.age, fencer.eliminated])


        

    def export_matches(self) -> list:
        match_results: List[dict] = []
        matches = []
        if self.stage == Stage.PRELIMINARY_ROUND:
            matches = self.matches_of_current_preliminary_round
        elif self.stage != Stage.GRAND_FINAL:
            matches = self.elimination_matches
        
        for match in matches:
            match_results.append({
                "id": match.id,
                "group": match.group,
                "red": match.red.short_str,
                "red_score": match.red_score,
                "green_score": match.green_score,
                "green": match.green.short_str,
                "match_started": match.match_ongoing_timestamp.strftime("%Y-%m-%d %H:%M:%S") if match.match_ongoing_timestamp else "-",
                "match_completed": match.match_completed_timestamp.strftime("%Y-%m-%d %H:%M:%S") if match.match_completed_timestamp else "-",
            })

        return match_results


    # ---| Simulation |---

    def simulate_current(self) -> None:
        if not self.simulation_active:
            raise TournamentError("Simulation is not active")

        for match in (self.matches_of_current_preliminary_round if self.stage == Stage.PRELIMINARY_ROUND else self.elimination_matches):

            if not match.match_completed:
                try:
                    if not match.match_ongoing or match.wildcard_or_disq:
                        self.set_active(match.id)

                    if not match.wildcard_or_disq:
                        score = (15, random.randint(0, 14)) if random.choice([True, False]) else (random.randint(0,14), 15)
                        self.push_score(match.id, *score)

                    progress = round((self.matches_of_current_preliminary_round.index(match) / len(self.matches_of_current_preliminary_round)) if self.stage == Stage.PRELIMINARY_ROUND else (self.elimination_matches.index(match) / len(self.elimination_matches)) * 20)
                    print(f"Simulating... |{'#' * progress}{' ' * (20 - progress)}|", end="\r")
                except Exception as e:
                    logger.error(e, exc_info=True)
                    continue

            time.sleep(0.01)

        print(f"Simulating... |{'#' * 20}|")
        logger.info("Simulation Done.")


    # ---| Bracket Class |---
    class Bracket:
        def __init__(self, matches: List[EliminationMatch], stage: Stage, title: str):
            self.nodes = []
            self.stages = [stage]
            for match in matches:
                self.nodes.append(self.Node(match, stage, root=True))
            self.title = title

        def create_new_round(self, matches: List[EliminationMatch], stage: Stage):
            self.stages.append(stage)
            nodes = [self.Node(match, stage) for match in matches]
            
            for node in nodes:
                for established_node in list(filter(lambda x: x.stage == stage.previous_stage(), self.nodes)):
                    if established_node.match.red in [node.match.red, node.match.green] or established_node.match.green in [node.match.red, node.match.green]:
                        established_node.assign_child(node)
                        node.assign_parent(established_node)
                        logger.debug(f"Assigned {node.match} to {established_node.match}")
                
            self.nodes.extend(nodes)


        def map(self):
            json_map = {
                "title": self.title,
            }

            temp_parents_stack = []

            stages_reversed = list(reversed(self.stages))

            for stage in stages_reversed:
                stage_map = []

                stage_list = list(filter(lambda x: x.stage == stage, self.nodes))

                if len(json_map) > 1:
                    # Sort in order of temp_child_stack
                    try:
                        stage_list = sorted(stage_list, key=lambda x: temp_parents_stack.index(x.id))
                    except ValueError:
                        logger.error(f"temp_parents_stack: {temp_parents_stack}")
                        logger.error(f"stage_list: {[node.id for node in stage_list]}")

                temp_parents_stack = []

                for node in stage_list:
                    stage_map.append(node.get_info())
                    if node.parents != []:
                        temp_parents_stack.extend([parents.id for parents in node.parents])
                        logger.debug(f"Added {[parents.id for parents in node.parents]} to temp_parents_stack")
                json_map[str(stage.value)] = stage_map
                json_map[str(stage.value)].append(stage.name.replace("_", " "))

            return json_map


        class Node:
            def __init__(self, match: EliminationMatch, stage: Stage, root: bool = False):
                self.id = random_generator.id(8)
                self.match = match
                self.stage = stage
                self.parents = []
                self.child = None
                self.root = root

            def assign_child(self, child):
                self.child = child

            def assign_parent(self, parent):
                self.parents.append(parent)

            def get_info(self):
                return {
                    "node_id": self.id,
                    "match_id": self.match.id,
                    "stage": self.stage.name,
                    "child": self.child.id if self.child else None,
                    "parents": [parent.id for parent in self.parents] if self.parents else None,
                    "root": self.root,
                    
                    "red": self.match.red.short_str,
                    "red_id": self.match.red.id,
                    "red_nationality": self.match.red.nationality,
                    "red_score": self.match.red_score,
                    "green": self.match.green.short_str,
                    "green_id": self.match.green.id,
                    "green_nationality": self.match.green.nationality,
                    "green_score": self.match.green_score,
                    "match_started": self.match.match_ongoing_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.match.match_ongoing_timestamp else "-",
                    "match_completed": self.match.match_completed_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.match.match_completed_timestamp else "-",
                }