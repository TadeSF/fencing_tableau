import datetime
from typing import Literal
import os
from exceptions import CSVError

def check_name(name: str):
    if name == "":
        raise ValueError("Name must be non-empty")
    if type(name) != str:
        raise ValueError("Name must be a string")

def check_club(club: str):
    if club == "":
        raise ValueError("Club must be non-empty")
    if type(club) != str:
        raise ValueError("Club must be a string")
    if len(club) > 5:
        raise ValueError("Club must be at most 5 characters long")

def check_nationality(value):
    if value == "":
        raise ValueError("Nationality must be non-empty")
    if type(value) != str:
        raise ValueError("Nationality must be a string")
    if len(value) != 0 and (len(value) != 3 or not value.isalpha() or not value.isupper()):
            raise CSVError(f"Nationality must be a valid alpha-3 format with all uppercase letters.")
    else:
        # Check if Flag exists
        if (value.lower() + ".svg") not in os.listdir("static/flags"):
            raise CSVError(f"Invalid flag (Flag '{value}' does not exist)")

def check_gender(value):
    if len(value) != 0 and value not in ['M', 'F', 'D']:
        raise CSVError(f"Gender must be either 'M' or 'F' or 'D'.")
    
def check_handedness(value):
    if len(value) != 0 and value not in ['R', 'L']:
        raise CSVError(f"Handedness must be either 'R' or 'L'.")

def check_age(value) -> str:
    current_year = datetime.datetime.now().strftime("%Y")

    if len(value) != 0:
        # Age must be either a positiv integer between 0 and 99, a 4-digit positiv integer between 1900 and datetime.datetime.now().strftime(%Y) or a string of the format 'YYYY-MM-DD'
        if value.isdigit() and len(value) == 2:
            if not (0 <= int(value) <= 99):
                raise CSVError(f"Age must be a positiv integer between 0 and 99.")
        elif value.isdigit() and len(value) == 4:
            if not (1900 <= int(value) <= current_year):
                raise CSVError(f"Age must be a 4-digit positiv integer between 1900 and {current_year}.")
            value = f"{int(current_year) - int(value)}"
        else:
            try:
                birthday = datetime.datetime.strptime(value, '%Y-%m-%d')
                value = f"{current_year - birthday.year - ((current_year, birthday.month, birthday.day) < (birthday.year, birthday.month, birthday.day))}"
            except ValueError:
                raise CSVError(f"Age must be either a positiv integer between 0 and 99, a 4-digit positiv integer between 1900 and {current_year} or a string of the format 'YYYY-MM-DD'.")
    
    return value


    
def check_attr(attr: Literal["name", "club", "nationality", "gender", "handedness", "age"], value):
    if attr == "name":
        check_name(value)
    elif attr == "club":
        check_club(value)
    elif attr == "nationality":
        check_nationality(value)
    elif attr == "gender":
        check_gender(value)
    elif attr == "handedness":
        check_handedness(value)
    elif attr == "age":
        check_age(value)
    else:
        raise ValueError("Invalid attribute")
