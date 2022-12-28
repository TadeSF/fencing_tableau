from fencer import Fencer
from match import Match

def read_fencer_csv_file(file_path: str) -> list:
    if file_path is None:
        file_path = input("Please enter the full path to the file you want to import from: \n")

    if not file_path.endswith(".csv"):
        file_path += ".csv"

    with open(file_path, "r") as f:
        csv_file = f.readlines()

    # Remove the first line (headers) if it exists
    if csv_file[0].startswith("Name"):
        csv_file.pop(0)
    
    # Create a dictionary of fencers
    fencers = []
    for line in csv_file:
        line = line.split(",")
        fencer_name = line[0].strip()
        fencer_club = line[1].strip()
        fencer_nationality = line[2].strip()
        fencers.append(Fencer(fencer_name, fencer_club if fencer_club != "" else None, fencer_nationality if fencer_nationality != "" else None))
    
    return fencers


def export_preliminary_matches(matches: list, file_path: str = None):
    if file_path is None:
        file_path = input("Please enter the full path to the file you want to export to: \n")

    with open(file_path, "w") as f:
        for match in matches:
            # TODO – Continue here
            f.write(f"{match.green.name},{match.red.name},{match.piste}\n")


def export_intermediate_matches(matches: list, file_path: str = None):
    if file_path is None:
        file_path = input("Please enter the full path to the file you want to export to: \n")

    with open(file_path, "w") as f:
        for match in matches:
            # TODO – Continue here
            f.write(f"{match.green.name},{match.red.name},{match.piste}\n")