import csv
from match import *
from tournament import *
from fencer import *

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify

# ------- Global Variables -------
tournament: Tournament = None



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
        if row[0] != 'Name':
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

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/matches')
def matches():
    return render_template('/dashboard/matches.html')

@app.route('/dashboard/matches/update', methods=['GET'])
def get_matches():
    global tournament
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_matches())

@app.route('/dashboard/matches/generate')
def generate_matches():
    global tournament
    tournament.generate_matches()
    # Return a 304 to prevent the page from reloading
    return '', 304

@app.route('/dashboard/matches/set_active', methods=['POST'])
def set_active():
    global tournament
    # Get the match id from application/json response
    match_id = request.json['id']
    tournament.set_active(match_id)
    # Return a 304 to prevent the page from reloading
    return '', 304

@app.route('/dashboard/matches/push_score', methods=['POST'])
def push_score():
    global tournament
    match_id = request.form['id']
    green_score = int(request.form['green_score'])
    red_score = int(request.form['red_score'])
    tournament.push_score(match_id, green_score, red_score)
    # Return a 304 to prevent the page from reloading
    return '', 304

@app.route('/dashboard/standings')
def standings():
    return render_template('/dashboard/standings.html')

@app.route('/dashboard/options')
def options():
    return render_template('/dashboard/options.html')

@app.route('/dashboard/standings/update', methods=['GET'])
def get_standings():
    global tournament
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_standings())









app.run(debug=True, port=8080)






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