import csv
from match import *
from tournament import *
from fencer import *

from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# ------- Global Variables -------
tournament = None



# ------- Flask -------
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    # render a template
    return render_template('index.html')

@app.route('/start_form')
def start_form():
    return render_template('start_form.html')

@app.route('/start_form', methods=['POST'])
def process_form():
    global tournament

    name = request.form['name']
    fencers_csv = request.files['fencers']
    location = request.form['location']
    date = request.form['date']
    first_elimination_round_raw = request.form['first_elimination_round']
    elimination_mode = request.form['elimination_mode']
    only_elimination = 'only_elimination' in request.form
    no_intermediate = 'no_intermediate' in request.form

    # do something with the form data

    fencers = []
    csv_contents = fencers_csv.read().decode('utf-8')
    reader = csv.reader(csv_contents.splitlines())
    for row in reader:
        print(row)
        fencers.append(Fencer(row[0], row[1], row[2]))

    if first_elimination_round_raw == '32th':
        first_elimination_round = 5
    elif first_elimination_round_raw == '16th':
        first_elimination_round = 4
    elif first_elimination_round_raw == 'QF':
        first_elimination_round = 3
    elif first_elimination_round_raw == 'SF':
        first_elimination_round = 2
    elif first_elimination_round_raw == 'Final':
        first_elimination_round = 1
    
    tournament = Tournament(name, fencers, location, date, first_elimination_round, elimination_mode.lower(), only_elimination, no_intermediate)

    print(tournament.name)
    print(tournament.fencers)
    print(tournament)

    return redirect(url_for('index'))


app.run(debug=True, port=5000)




# ------- Sample Data -------
# sample_name = "Test Tournament"
# sample_date = "2020-01-01"
# sample_location = "Test Location"
# sample_fencers_raw = csv.reader(open('tib.csv', 'r'))
# sample_fencers = []

# for fencer in sample_fencers_raw:
#     sample_fencers.append(Fencer(fencer[0], fencer[1], fencer[2]))

# sample_stage = "Preliminary Round"

# sample_matches = [
#     {
#         "id": "AH19JL",
#         "group": "A",
#         "piste": 1,

#         "green": "Tade Strehk",
#         "green_flag": open('flags/deu.svg', 'r').read(),
#         "green_score": 5,

#         "red": "Olga Iwnanowska",
#         "red_flag": open('flags/pol.svg', 'r').read(),
#         "red_score": 3,

#         "done": True,
#     },
#     {
#         "id": "K729JV",
#         "group": "B",
#         "piste": 2,
        
#         "green": "Tade Strehk",
#         "green_flag": open('flags/mex.svg', 'r').read(),
#         "green_score": 5,

#         "red": "Olga Iwnanowska",
#         "red_flag": open('flags/svn.svg', 'r').read(),
#         "red_score": 3,
        
#         "done": True,
#     }
# ]

# sample_standings = [
#     {
#         "rank": 1,
#         "name": "Tade Strehk",
#         "club": "TIB",
#         "nationality": "DEU",
#         "flag": open('flags/deu.svg', 'r').read(),
#         "win_percentage": 0.75,
#         "win_lose": "5 - 1",
#         "point_difference": "+4",
#         "points_for": 15,
#         "points_against": 11,
#     },
#     {
#         "rank": 2,
#         "name": "Olga Iwnanowska",
#         "club": "UP",
#         "nationality": "POL",
#         "flag": open('flags/pol.svg', 'r').read(),
#         "win_percentage": 0.5,
#         "win_lose": "5-3",
#         "point_difference": "-2",
#         "points_for": 20,
#         "points_against": 22,
#     },
# ]

# ------- Functionality -------

# def define_tournament():
#     # tournament = Tournament(sample_name, sample_fencers, sample_date, sample_location)
#     pass









# ------- Basic Program -------



# Welcome
# print("Welcome to the Fencing Tournament Manager!")
# print("This program is currently in development and is not ready for use.")




# 1. Create a tournament
# Initialize a tournament with a name, date, location and a list of fencers (CSV, ...) in the UI
# Then the tournament is created and the fencers are added to the tournament

# tournament = Tournament(sample_name, sample_fencers, sample_date, sample_location)

# 2. Create the preliminary round
# The preliminary round is created with the tournament object
# The preliminary round is a list of matches

# tournament.create_preliminary_round()
    # 3. Start the preliminary round
    # eel.update_matches(sample_matches, sample_stage)()
    # eel.update_standings(sample_standings, sample_stage)()