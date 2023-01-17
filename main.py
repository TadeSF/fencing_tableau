import csv
import datetime
import os
from match import GroupMatch, EliminationMatch
from tournament import *
from fencer import Fencer, Wildcard, Stage
from piste import PisteError, Piste
import random_generator

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, abort

# ------- Tournament Cache -------
tournament_cache: list[Tournament] = []

def get_tournament(tournament_id) -> Tournament | None:
    """
    This function returns a tournament from the tournament cache, given an id.
    If the tournament with the given id does not exist, it returns None.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament to be returned.

    Returns
    -------
    Tournament object
        if the tournament exists
    None
        if the tournament does not exist
    """

    global tournament_cache
    for tournament in tournament_cache:
        if tournament.id == tournament_id:
            return tournament
    return None

def check_tournament_exists(tournament_id) -> bool:
    """
    This function checks if a tournament with given id exists in the tournament cache.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament to be checked.
    
    Returns
    -------
    True
        if the tournament exists
    False
        if the tournament does not exist
    """
    global tournament_cache
    for tournament in tournament_cache:
        if tournament.id == tournament_id:
            return True
    return False


# ------- Pickeling -------
# Pickeling is an easy way to save data to a file, so that it stays persistent even if the server has to restart.

import pickle

def save_tournament(tournament: Tournament):
    """
    This function saves a tournament to a file, so that it can be loaded again later, even if the server has to restart.
    This is done by pickeling a tournament object. The file is saved in the /tournaments folder and is named after the tournament id.

    Parameters
    ----------
    tournament : Tournament
        The tournament to be saved.
    """
    with open(f'tournaments/{tournament.id}.pickle', 'wb') as f:
        pickle.dump(tournament, f)

def load_all_tournaments():
    """
    This function loads all saved tournaments from the /tournaments folder and adds them to the tournament cache.
    """
    global tournament_cache
    for file in os.listdir('tournaments'):
        if file.endswith('.pickle'):
            with open(f'tournaments/{file}', 'rb') as f:
                tournament = pickle.load(f)
                if tournament is not None:
                    tournament_cache.append(tournament)

def delete_old_tournaments():
    """
    This function deletes all tournament files that are older than 1 day from the /tournaments folder.
    """
    global tournament_cache
    for tournament in tournament_cache:
        # Delete the tournament.pickle file if it is older than 1 day
        if (datetime.datetime.now() - tournament.created_at).days > 1:
            os.remove(f'tournaments/{tournament.id}.pickle')
            tournament_cache.remove(tournament)



# ------- Searches -------
def search_fencer(tournament_id, fencer_id) -> Fencer | None:
    """
    This function searches for a fencer in a tournament, given the tournament id and the fencer id.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament to be searched in.
    fencer_id : str
        The id of the fencer to be searched for.

    Returns
    -------
    Fencer object
        if the fencer exists
    None
        if the fencer does not exist
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return None
    for fencer in tournament.fencers:
        if fencer.id == fencer_id:
            return fencer
    return None




# ------- Flask -------
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/favicon.ico')
def favicon():
    """
    Flask serves on GET request /favicon.ico the favicon.ico file from the static folder.

    Returns
    -------
    send_from_directory(favicon.ico)
    """
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    """
    Flask serves on GET request / the index.html file from the templates folder.
    """
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process_form():
    """
    Start a new Tournament:
    Flask processes a POST request that contains infos on a new tournament.
    It creates a new tournament object and adds it to the tournament cache as well as saving it to a file.

    Parameters
    ----------
    name : str
        The name of the tournament.
    fencers : file
        A csv file containing the fencers with the Headers Name, Club, Nationality, Gender, Handedness. Nationality has to be the alpha-3 Countrycode. Gender and Handedness are optional.
    location : str
        The location of the tournament.
    pistes : int
        The number of pistes.
    first_elimination_round : int
        The first elimination round (by default, this will be calculated automaticly)
    elimination_mode : str
        The elimination mode (manager can choose between "KO", "Placement" or "Repechage")
    preliminary_rounds : int
        The number of preliminary rounds.
    preliminary_groups : int
        The number of preliminary groups (by default, this will be calculated automaticly)

    Returns
    -------
    redirects to /dashboard/<tournament_id>
    """

    global tournament_cache

    name = request.form['name']
    fencers_csv = request.files['fencers']
    location = request.form['location']
    num_pistes = request.form['pistes']
    first_elimination_round = request.form['first_elimination_round']
    elimination_mode = request.form['elimination_mode']
    preliminary_rounds = request.form['number_of_preliminary_rounds']
    preliminary_groups = request.form['number_of_preliminary_groups']

    # --- Process the data from the form
    # Process csv file

    fencers = []
    csv_contents = fencers_csv.read().decode('utf-8')
    reader = csv.reader(csv_contents.splitlines())
    i = 1


    for row in reader:
        if row[0] != 'Name':
            fencer_name = row[0]
            fencer_club = row[1]
            fencer_nationality = row[2]
            fencer_gender = row[3] if len(row) > 3 else None
            fencer_handedness = row[4] if len(row) > 4 else None

            fencers.append(Fencer(fencer_name, fencer_club, fencer_nationality, fencer_gender, fencer_handedness, i, int(preliminary_rounds)))
            i += 1

    # Generate and save the new tournament

    random_id = random_generator.id(6)
    
    tournament = Tournament(random_id, name, fencers, location, preliminary_rounds, preliminary_groups, first_elimination_round, elimination_mode.lower(), num_pistes)
    tournament_cache.append(tournament)
    save_tournament(tournament)

    return redirect(url_for('dashboard', tournament_id=random_id))

@app.route('/login-manager', methods=['POST'])
def login_manager():
    """
    Flask processes a POST request to login as a manager.
    Note: This is not implemented fully yet.

    Returns
    -------
    redirects to /dashboard/<tournament_id>, 200
        On success
    404
        On tournament not found
    """
    global tournament_cache
    tournament_id = request.form['tournament_id']
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return redirect(url_for('dashboard', tournament_id=tournament_id))

@app.route('/login-fencer', methods=['POST'])
def login_fencer():
    """
    Flask processes a POST request to login as a fencer.
    Note: This is not implemented yet.

    Returns
    -------
    404
    """
    # TODO Implement
    abort(404)

@app.route('/login-referee', methods=['POST'])
def login_referee():
    """
    Flask processes a POST request to login as a referee.
    Note: This is not implemented yet.

    Returns
    -------
    404
    """
    # TODO Implement
    abort(404)

@app.route('/<tournament_id>/dashboard')
def dashboard(tournament_id):
    """
    Flask serves on GET request /<tournament_id>/dashboard the dashboard.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    dashboard.html 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return render_template('dashboard.html', tournament_id=tournament_id)

@app.route('/<tournament_id>/dashboard/update', methods=['GET'])
def get_dashboard_infos(tournament_id):
    """
    Flask serves on GET request /<tournament_id>/dashboard/update the dashboard infos as a json object.
    This includes general information about the tournament.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    json object (from tournament.get_dashboard_infos()), 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        tournament = get_tournament(tournament_id)
    return jsonify(tournament.get_dashboard_infos())

@app.route('/<tournament_id>/matches')
def matches(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/matches the matches.html file from the templates folder.
    This is the page where the matches are displayed and it is visible on the dashboard as an iframe and can be opened in fullscreen.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    matches.html, 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return render_template('/dashboard/matches.html')

@app.route('/<tournament_id>/matches/update', methods=['GET'])
def get_matches(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/matches/update all matches of the current state as a json object.
    
    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    json object (from tournament.get_matches())
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_matches())

@app.route('/<tournament_id>/matches/set_active', methods=['POST'])
def set_active(tournament_id):
    """
    Flask processes a POST request to set a certain match as active.

    .. warning::
    The function will return a 400 Error Code, when the Piste that was assigned to the Match
    is still in use by another match.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    match_id : str
        The id of the match.
    
    Returns
    -------
    200 (on success)
    400 (on PisteError)
    """
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
    """
    Flask processes a POST request to push a score of a finished match.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    match_id : str
        The id of the match.
    green_score : int
        The score of the green fencer.
    red_score : int
        The score of the red fencer.
    
    Returns
    -------
    200
    """
    tournament = get_tournament(tournament_id)
    match_id = request.form['id']
    green_score = int(request.form['green_score'])
    red_score = int(request.form['red_score'])
    tournament.push_score(match_id, green_score, red_score)
    save_tournament(tournament)
    return '', 200

@app.route('/<tournament_id>/standings')
def standings(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/standings the standings.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    standings.html, 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return render_template('/dashboard/standings.html')

@app.route('/<tournament_id>/standings/update', methods=['GET'])
def get_standings(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/standings/update the standings of the current state as a json object.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    json object (from tournament.get_standings()
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_standings())

@app.route('/<tournament_id>/matches-left', methods=['GET'])
def matches_left(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/matches-left the number of matches left in the current stage as a string.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    
    Returns
    -------
    str (from tournament.get_matches_left()
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return get_tournament(tournament_id).get_matches_left()

@app.route('/<tournament_id>/next-stage')
def next_stage(tournament_id):
    """
    Flask processes a GET request to go to the next stage.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        get_tournament(tournament_id).next_stage()
        return '', 200


@app.route('/<tournament_id>/fencer/<fencer_id>')
def fencer(tournament_id, fencer_id):
    """
    Flask serves on a GET request /<tournament_id>/fencer/<fencer_id> the fencer.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    fencer_id : str
        The id of the fencer.

    Returns
    -------
    fencer.html, 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        tournament = get_tournament(tournament_id)
        fencer = tournament.get_fencer_object(fencer_id)
        if fencer is None:
            abort(404)
        else:
            return render_template('/fencer.html',
                name=fencer.short_str,
                club=fencer.club,
                )


@app.route('/<tournament_id>/fencer/<fencer_id>/update', methods=['GET'])
def get_fencer(tournament_id, fencer_id):
    """
    Flask serves on a GET request /<tournament_id>/fencer/<fencer_id>/update the fencer object as a json object.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    fencer_id : str
        The id of the fencer.

    Returns
    -------
    json object (from tournament.get_fencer_object()
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([])
    return jsonify(tournament.get_fencer_hub_information(fencer_id))




@app.route('/<tournament_id>/simulate-current')
def simulate_current(tournament_id):
    """
    Flask processes a GET request to simulate all matches of the current stage.
    This is only used for testing purposes and will be deprecated in later versions.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        get_tournament(tournament_id).simulate_current()
        return '', 200



@app.errorhandler(404)
def page_not_found(e):
    """
    404 Error handler: Flask serves on a 404 Error the 404.html file from the templates folder.
    """
    return render_template('404.html'), 404




if __name__ == '__main__':
    load_all_tournaments()
    delete_old_tournaments()
    app.run(debug=True, port=8080)