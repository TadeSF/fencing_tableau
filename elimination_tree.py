import itertools
from fencer import *
from match import *


class EliminationTree():
    def __init__(self, fencers: list) -> None:

        # Fencer information
        self.fencers = fencers            
        if len(fencers) > 32:
            # Check if there are too many fencers
            raise ValueError("Too many fencers for elimination tree")
        self.eliminated_fencers = []

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