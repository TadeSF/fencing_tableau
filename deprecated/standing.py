from fencer import *
from match import *
import copy

class Standings:
    def __init__(self, fencers: list, copy_fencers: bool = True) -> None:
        self.copied = copy_fencers
        if self.copied:
            self.fencers = copy.deepcopy(fencers)
        else:
            self.fencers = fencers

        self.overall = self.sort_overall()

        self.prelim = self.sort_prelim()
        self.prelim_groups = self.sort_prelim_groups()

        self.intermediate = self.sort_intermediate()
        self.intermediate_groups = self.sort_intermediate_groups()

        self.elimination = self.sort_elimination()
        
        self.combined = self.sort_combined()

        self.update_rank()


        
        
    def sort_overall(self) -> list:
        # sort by win percentage, points difference, points for, points against
        return sorted(self.fencers, key=lambda fencer: (fencer.win_percentage(), fencer.points_difference(), fencer.statistics["overall"]["points_for"], fencer.statistics["overall"]["points_against"]), reverse=True)

    def sort_prelim(self) -> list:
        fencers = [fencer for fencer in self.fencers if fencer.statistics["preliminary"]["matches"] > 0]
        return sorted(fencers, key=lambda fencer: (fencer.win_percentage("preliminary"), fencer.points_difference("preliminary"), fencer.statistics["preliminary"]["points_for"], fencer.statistics["preliminary"]["points_against"]), reverse=True)


    def sort_intermediate(self) -> list:
        fencers = [fencer for fencer in self.fencers if fencer.statistics["intermediate"]["matches"] > 0]
        return sorted(fencers, key=lambda fencer: (fencer.win_percentage("intermediate"), fencer.points_difference("intermediate"), fencer.statistics["intermediate"]["points_for"], fencer.statistics["intermediate"]["points_against"]), reverse=True)


    def sort_elimination(self) -> list:
        fencers = [fencer for fencer in self.fencers if fencer.statistics["elimination"]["matches"] > 0]

        first_four = [fencer for fencer in self.fencers if fencer.podium != None]
        first_four.sort(key=lambda fencer: fencer.podium)
        fencers.sort(key=lambda fencer: (fencer.statistics["elimination"]["wins"], fencer.statistics["elimination"]["matches"], fencer.statistics["elimination"]["points_difference"], fencer.statistics["elimination"]["points_for"], fencer.statistics["elimination"]["points_against"]), reverse=True)
        
        ranking = first_four

        for fencer in fencers:
            if fencer not in first_four:
                ranking.append(fencer)
        
        return ranking


    def sort_prelim_groups(self) -> dict:
        prelim_groups = {}

        for fencer in self.prelim if self.prelim != None else []:
            if fencer.prelim_group not in prelim_groups:
                prelim_groups[fencer.prelim_group] = []
            prelim_groups[fencer.prelim_group].append(fencer)
        
        return prelim_groups


    def sort_intermediate_groups(self) -> dict:
        intermediate_groups = {}


        for fencer in self.intermediate if self.intermediate != None else []:
            if fencer.intermediate_group not in intermediate_groups:
                intermediate_groups[fencer.intermediate_group] = []
            intermediate_groups[fencer.intermediate_group].append(fencer)
        
        return intermediate_groups


    def sort_combined(self) -> dict:
        combined = {
            "Direct Elimination": [],
            "Intermediate Round": [],
            "Preliminary Round": []
            }

        combined["Direct Elimination"] = self.sort_elimination()

        intermediate = self.sort_intermediate()

        for fencer in intermediate:
            if fencer not in combined["Direct Elimination"]:
                combined["Intermediate"].append(fencer)

        preliminary = self.sort_prelim()
        
        for fencer in preliminary:
            if fencer not in combined["Direct Elimination"] and fencer not in combined["Intermediate Round"]:
                combined["Preliminary Round"].append(fencer)

        return combined


    def update_rank(self) -> None:
        for fencer in self.fencers:
            fencer.rank["preliminary"] = self.prelim.index(fencer) + 1
            fencer.rank["intermediate"] = self.intermediate.index(fencer) + 1
            fencer.rank["elimination"] = self.elimination.index(fencer) + 1
            fencer.rank["overall"] = self.overall.index(fencer) + 1

            combined_standings_list = []
            for fencer in self.combined["Direct Elimination"]:
                combined_standings_list.append(fencer)
            for fencer in self.combined["Intermediate Round"]:
                combined_standings_list.append(fencer)
            for fencer in self.combined["Preliminary Round"]:
                combined_standings_list.append(fencer)
            fencer.rank["combined"] = combined_standings_list.index(fencer) + 1



    def calculate_advancing_fencers(self):
        intermediate_needed = None

        if self.prelim == None:
            raise ValueError("At least preliminary round must be completed before calculating advancing fencers")

        elif self.intermediate == None:
            # calculate advancing fencers from preliminary round
            # If a round of "only" 32 fencers doesn't eliminate a third of all fencers, then the intermediate round will be skipped
            if len(self.fencers) <= 32 or len(self.fencers) - 32 < len(self.fencers) / 3:
                intermediate_needed = False
            else:
                intermediate_needed = True                
                

        if intermediate_needed == False or (self.intermediate != None and self.elimination == None):
            # calculate advancing fencers from intermediate round
            if len(self.fencers) <= 32:
                # 32 fencers or less, all fencers advance to elimination round
                advancing_fencers = self.fencers

            elif len(self.fencers) - 32 < len(self.fencers) / 3:
                # if the intermediate round doesn't eliminate a third of all fencers, then the elimination round will be skipped
                # the best 32 fencers advance to elimination round
                advancing_fencers = self.prelim[:32]
            
            else:
                advancing_fencers = self.intermediate[:32]
        
            for fencer in self.fencers:
                if fencer in advancing_fencers:
                    fencer.stage = "elimination"

                





    def print_single_place(self, place: int, fencer: Fencer, with_stats: bool = True, stage: Literal["preliminary", "intermediate", "elimination", "overall"] = None) -> str:
        string = f"{place}. {fencer.name} ({fencer.nationality} / {fencer.club})\n"
        if with_stats:
            if stage == None:
                raise ValueError("Stage must be specified if with_stats is True")
            else:
                string += f"     W/L: {fencer.statistics[stage]['wins']}/{fencer.statistics[stage]['losses']} ({fencer.win_percentage(stage) * 100}%)\n     P: {fencer.statistics[stage]['points_for']}:{fencer.statistics[stage]['points_against']} ({fencer.points_difference(stage)})\n\n"
        return string


    def print_standings(self, stage: Literal["preliminary", "intermediate", "elimination", "overall", "combined"] = "combined", groups: bool = False, with_stats: bool = True) -> str:
        if stage == "combined":
            string = "\n\nStandings after Final"
            string += "\n---------------------\n\n"
            string += "--- Direct Elimination\n\n"
            string += "First Place:\n"
            string += self.print_single_place(1, self.combined["Direct Elimination"][0])
            string += "\n\nSecond Place:\n"
            string += self.print_single_place(2, self.combined["Direct Elimination"][1])
            string += "\n\nThird Place:\n"
            string += self.print_single_place(3, self.combined["Direct Elimination"][2])
            string += "\n\n"

            placement_counter = 4

            for fencer in self.combined["Direct Elimination"][3:]:
                string += self.print_single_place(placement_counter, fencer, with_stats, "overall")
                string += "\n\n"
                placement_counter += 1
            string += "\n\n"
            if len(self.combined["Intermediate Round"]) > 0:
                string += "\n\n--- Intermediate Round\n\n"
                for fencer in self.combined["Intermediate Round"]:
                    string += self.print_single_place(placement_counter, fencer, with_stats, "overall")
                    string += "\n\n"
                    placement_counter += 1
            else:
                string += "\n\n     -> No intermediate round"
            string += "\n\n"
            string += "\n\n--- Preliminary Round\n\n"
            if len(self.combined["Preliminary Round"]) > 0:
                for fencer in self.combined["Preliminary Round"]:
                    string += self.print_single_place(placement_counter, fencer, with_stats, "overall")
                    placement_counter += 1
            else:
                string += "\n\n     -> No preliminary round"
            string += "\n\n"

        elif stage == "overall":
            string = "\n\Overall Standings by Performance"
            string += "\n---------------------\n\n"
            for i, fencer in enumerate(self.sort_elimination()):
                string += self.print_single_place(i + 1, fencer, with_stats, "overall")
            string += "\n\n"

        elif stage == "elimination":
            string = "\n\nDirect Elimination Standings"
            string += "\n---------------------\n\n"
            for i, fencer in enumerate(self.sort_elimination()):
                string += self.print_single_place(i + 1, fencer, with_stats, "elimination")
            string += "\n\n"
        
        elif stage == "intermediate":
            if groups:
                intermediate_groups = self.sort_intermediate_groups()
                for group in intermediate_groups:
                    string = f"\n\nIntermediate Round Standings for Group {group}"
                    string += "\n---------------------\n\n"
                    for i, fencer in enumerate(intermediate_groups[group]):
                        string += self.print_single_place(i + 1, fencer, with_stats, "intermediate")
                    string += "\n\n"
            else:
                string = "\n\nIntermediate Round Standings"
                string += "\n---------------------\n\n"
                for i, fencer in enumerate(self.sort_intermediate()):
                    string += self.print_single_place(i + 1, fencer, with_stats, "intermediate")
                string += "\n\n"
        
        elif stage == "preliminary":
            if groups:
                prelim_groups = self.sort_prelim_groups()
                for group in prelim_groups:
                    string = f"\n\nPreliminary Round Standings for Group {group}"
                    string += "\n---------------------\n\n"
                    for i, fencer in enumerate(prelim_groups[group]):
                        string += self.print_single_place(i + 1, fencer, with_stats, "preliminary")
                    string += "\n\n"
            else:
                string = "\n\nPreliminary Round Standings"
                string += "\n---------------------\n\n"
                for i, fencer in enumerate(self.sort_prelim()):
                    string += self.print_single_place(i + 1, fencer, with_stats, "preliminary")
                string += "\n\n"

        return string




