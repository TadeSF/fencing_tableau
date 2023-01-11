import csv
import datetime
import os
from match import *
from tournament import *
from fencer import *
from piste import PisteError, Piste

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify

# ------- Tournament Cache -------
tournament_cache: list[Tournament] = []

def get_tournament(tournament_id) -> Tournament:
    global tournament_cache
    for tournament in tournament_cache:
        if tournament.id == tournament_id:
            return tournament
    return None

def check_tournament_exists(tournament_id) -> bool:
    global tournament_cache
    for tournament in tournament_cache:
        if tournament.id == tournament_id:
            return True
    return False


# ------- Pickeling -------
# Pickeling is an easy way to save data to a file, so that it stays persistent even if the server has to restart.

import pickle

def save_tournament(tournament: Tournament):
    with open(f'tournaments/{tournament.id}.pickle', 'wb') as f:
        pickle.dump(tournament, f)

def load_all_tournaments():
    global tournament_cache
    for file in os.listdir('tournaments'):
        if file.endswith('.pickle'):
            with open(f'tournaments/{file}', 'rb') as f:
                tournament = pickle.load(f)
                tournament_cache.append(tournament)

def delete_old_tournaments():
    global tournament_cache
    for tournament in tournament_cache:
        # Delete the tournament.pickle file if it is older than 1 day
        if (datetime.datetime.now() - tournament.created_at).days > 1:
            os.remove(f'tournaments/{tournament.id}.pickle')
            tournament_cache.remove(tournament)




# ------- Flask -------
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    # render a template
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process_form():
    global tournament_cache

    name = request.form['name']
    fencers_csv = request.files['fencers']
    location = request.form['location']
    num_pistes = request.form['pistes']
    first_elimination_round = request.form['first_elimination_round']
    elimination_mode = request.form['elimination_mode']
    preliminary_rounds = request.form['number_of_preliminary_rounds']
    preliminary_groups = request.form['number_of_preliminary_groups']

    # do something with the form data

    fencers = []
    csv_contents = fencers_csv.read().decode('utf-8')
    reader = csv.reader(csv_contents.splitlines())
    i = 1
    for row in reader:
        if row[0] != 'Name':
            fencers.append(Fencer(row[0], row[1], row[2], i, int(preliminary_rounds)))
            i += 1


    random_id = random_generator.id(6)
    
    tournament = Tournament(random_id, name, fencers, location, preliminary_rounds, preliminary_groups, first_elimination_round, elimination_mode.lower(), num_pistes)
    tournament_cache.append(tournament)
    save_tournament(tournament)

    return redirect(url_for('dashboard', tournament_id=random_id))

@app.route('/login-manager', methods=['POST'])
def login_manager():
    global tournament_cache
    tournament_id = request.form['tournament_id']
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        return redirect(url_for('dashboard', tournament_id=tournament_id))

@app.route('/login-fencer', methods=['POST'])
def login_fencer():
    # TODO Implement
    return 404

@app.route('/login-referee', methods=['POST'])
def login_referee():
    # TODO Implement
    return 404

@app.route('/<tournament_id>/dashboard')
def dashboard(tournament_id):
    if not check_tournament_exists(tournament_id):
        return redirect(url_for('index'))
    else:
        return render_template('dashboard.html', tournament_id=tournament_id)

@app.route('/<tournament_id>/dashboard/update', methods=['GET'])
def get_dashboard_infos(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        tournament = get_tournament(tournament_id)
    return jsonify(tournament.get_dashboard_infos())

@app.route('/<tournament_id>/matches')
def matches(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        return render_template('/dashboard/matches.html')

@app.route('/<tournament_id>/matches/update', methods=['GET'])
def get_matches(tournament_id):
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_matches())

@app.route('/<tournament_id>/matches/set_active', methods=['POST'])
def set_active(tournament_id):
    try:
        tournament = get_tournament(tournament_id)
        # Get the match id from application/json response
        match_id = request.json['id']
        tournament.set_active(match_id)
        save_tournament(tournament)
        return '', 200
    except PisteError:
        return '', 400

@app.route('/<tournament_id>/matches/push_score', methods=['POST'])
def push_score(tournament_id):
    tournament = get_tournament(tournament_id)
    match_id = request.form['id']
    green_score = int(request.form['green_score'])
    red_score = int(request.form['red_score'])
    tournament.push_score(match_id, green_score, red_score)
    save_tournament(tournament)
    # Return a 304 to prevent the page from reloading
    return '', 304

@app.route('/<tournament_id>/standings')
def standings(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        return render_template('/dashboard/standings.html')

@app.route('/<tournament_id>/standings/update', methods=['GET'])
def get_standings(tournament_id):
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_standings())

@app.route('/<tournament_id>/matches-left', methods=['GET'])
def matches_left(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        return get_tournament(tournament_id).get_matches_left()

@app.route('/<tournament_id>/next-stage')
def next_stage(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        get_tournament(tournament_id).next_stage()
        return '', 200



@app.route('/<tournament_id>/simulate-current')
def simulate_current(tournament_id):
    if not check_tournament_exists(tournament_id):
        return '', 404
    else:
        get_tournament(tournament_id).simulate_current()
        return '', 200









load_all_tournaments()
delete_old_tournaments()
app.run(debug=True, port=8080)