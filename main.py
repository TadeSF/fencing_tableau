try:
    import csv
    import datetime
    import os
    import traceback
    import logging
    import threading
    from typing import List, Literal

    from flask import   (Flask, Request, Response, abort, jsonify, make_response,
                        redirect, render_template, request, send_file,
                        send_from_directory, url_for)

    import random_generator
    from exceptions import *
    from fencer import Fencer, Stage, Wildcard
    from match import EliminationMatch, GroupMatch
    from piste import Piste, PisteError
    from tournament import *

except ModuleNotFoundError:
    raise RequiredLibraryError("Please install all required libraries by running 'pip install -r requirements.txt'")


# ------- Tournament Cache -------
tournament_cache: List[Tournament] = []
cache_lock = threading.Lock()

def get_tournament(tournament_id) -> Tournament:
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

    global tournament_cache, cache_lock
    with cache_lock:
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
    global tournament_cache, cache_lock
    with cache_lock:
        for tournament in tournament_cache:
            if tournament.id == tournament_id:
                return True
        return False


# ------- Pickeling -------
# Pickeling is an easy way to save data to a file, so that it stays persistent even if the server has to restart.

import pickle
import subprocess


def create_local_tournament_folder():
    """
    This function creates a folder called "tournaments" in the root directory, if it does not already exist.
    """
    if not os.path.exists('tournament_cache'):
        os.makedirs('tournament_cache')

def save_tournament(tournament: Tournament):
    """
    This function saves a tournament to a file, so that it can be loaded again later, even if the server has to restart.
    This is done by pickeling a tournament object. The file is saved in the /tournaments folder and is named after the tournament id.

    Parameters
    ----------
    tournament : Tournament
        The tournament to be saved.
    """
    create_local_tournament_folder()
    with open(f'tournament_cache/{tournament.id}.pickle', 'wb') as f:
        pickle.dump(tournament, f)

def load_all_tournaments():
    """
    This function loads all saved tournaments from the /tournaments folder and adds them to the tournament cache.
    """
    global tournament_cache, cache_lock
    with cache_lock:
        create_local_tournament_folder()
        for file in os.listdir('tournament_cache'):
            if file.endswith('.pickle'):
                with open(f'tournament_cache/{file}', 'rb') as f:
                    tournament = pickle.load(f)
                    if tournament is not None:
                        tournament_cache.append(tournament)

def delete_old_tournaments():
    """
    This function deletes all tournament files that are older than 1 day from the /tournaments folder.
    """
    global tournament_cache, cache_lock
    with cache_lock:
        create_local_tournament_folder()
        for tournament in tournament_cache:
            # Delete the tournament.pickle file if it is older than 1 day
            if (datetime.datetime.now() - tournament.created_at).days > 1:
                os.remove(f'tournament_cache/{tournament.id}.pickle')
                tournament_cache.remove(tournament)


# ------- Credentials -------
def save_master_credentials(tournament_id: str, password: str):
    """
    """
    # if txt file "credentials.txt" does not exist, create it
    if not os.path.exists('credentials.txt'):
        with open('credentials.txt', 'w') as f:
            f.write('')
    # if txt file "credentials.txt" exists, append the new credentials
    with open('credentials.txt', 'a') as f:
        f.write(f'{tournament_id}:{password}')


# ------- Login-Cookies -------
def create_master_cookie(response: Response, tournament_id: str) -> Response:
    """
    """
    response.set_cookie('logged_in_master', 'true', max_age=60*60*24)
    response.set_cookie('tournament', tournament_id, max_age=60*60*24)
    return response

def create_referee_cookie(response: Response, tournament_id: str) -> Response:
    """
    """
    response.set_cookie('logged_in_referee', 'true', max_age=60*60*24)
    response.set_cookie('tournament', tournament_id, max_age=60*60*24)
    return response

def create_fencer_cookie(response: Response, tournament_id: str, fencer_id: str) -> Response:
    """
    """
    response.set_cookie('logged_in_fencer', 'true', max_age=60*60*24)
    response.set_cookie('tournament', tournament_id, max_age=60*60*24)
    response.set_cookie('fencer', fencer_id, max_age=60*60*24)
    return response

def check_logged_in_as_master(request: Request, tournament_id: str) -> bool:
    """
    """
    if 'logged_in_master' in request.cookies:
        if "tournament" in request.cookies:
            if request.cookies['tournament'] == tournament_id:
                print("Logged in")
                return True
    print("Not logged in")
    return False

def check_logged_in_as_referee(request: Request, tournament_id: str) -> bool:
    """
    """
    if 'logged_in_referee' in request.cookies:
        if "tournament" in request.cookies:
            if request.cookies['tournament'] == tournament_id:
                print("Logged in")
                return True
    print("Not logged in")
    return False

def check_logged_in_as_fencer(request: Request, tournament_id: str, fencer_id: str) -> bool:
    """
    """
    if 'logged_in_fencer' in request.cookies:
        if "tournament" in request.cookies:
            if request.cookies['tournament'] == tournament_id:
                if "fencer" in request.cookies:
                    if request.cookies['fencer'] == fencer_id:
                        return True
    return False


# ------- Searches -------
def search_fencer(tournament_id, fencer_id) -> Fencer:
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


# ------- CSV -------

def check_csv(file) -> list:
    headers = next(file)
    body = []
    if headers != ['Name', 'Club', 'Nationality', 'Gender', 'Handedness', 'Age']:
        print(headers)
        raise CSVError(f"Invalid headers\n\nMust be {['Name', 'Club', 'Nationality', 'Gender', 'Handedness', 'Age']}")
    current_year = datetime.datetime.now().year
    row_number = 0
    for row in file:
        row_number += 1
        if len(row) != 6:
            raise CSVError(f"Invalid number of columns in row {row_number}")
        name, club, nationality, gender, handedness, age = row
        if len(nationality) != 0 and (len(nationality) != 3 or not nationality.isalpha() or not nationality.isupper()):
            raise CSVError(f"Nationality must be a valid alpha-3 format with all uppercase letters in row {row_number}")
        if len(gender) != 0 and gender not in ['M', 'F', 'D']:
            raise CSVError(f"Gender must be either 'M' or 'F' or 'D' in row {row_number}")
        if len(handedness) != 0 and handedness not in ['R', 'L']:
            raise CSVError(f"Handedness must be either 'R' or 'L' in row {row_number}")
        if len(age) != 0:
            if not age.isdigit():
                raise CSVError(f"Age must be a positive integer not larger than 100 or a 4-digit integer representing the birth year between 1900 and the current year in row {row_number}")
            age = int(age)
            if age > 100 and (age < 1900 or age > current_year):
                raise CSVError(f"Age must be a positive integer not larger than 100 or a 4-digit integer representing the birth year between 1900 and the current year in row {row_number}")
        body.append(row)

    if len(body) < 3:
        raise CSVError(f"CSV file does not contain enough (or any) fencers")
    
    return body



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

@app.route('/imprint')
def imprint():
    """
    """
    return render_template('imprint.html')

@app.route('/privacy')
def privacy():
    """
    """
    return render_template('privacy.html')

@app.route('/csv-template')
def csv_template_download():
    """
    """
    try:
        return send_file("static/template.csv", as_attachment=True)
    except Exception as e:
        return str(e)

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
    password = request.form['master_password']

    # --- Process the data from the form
    # Process csv file

    fencers = []
    csv_contents = fencers_csv.read().decode('utf-8')
    reader = csv.reader(csv_contents.splitlines())
    try:
        fencer_data = check_csv(reader)
    except CSVError as e:
        return jsonify({'success': False, 'error': 'CSV Error', 'message': str(e)})

    i = 1
    try:
        for row in fencer_data:
            fencer_name = row[0]
            fencer_club = row[1]
            fencer_nationality = row[2]
            fencer_gender = row[3] if row[3] != '' else None
            fencer_handedness = row[4] if row[4] != '' else None
            fencer_age = row[5] if row[5] != '' else None

            fencers.append(Fencer(fencer_name, fencer_club, fencer_nationality, fencer_gender, fencer_handedness, fencer_age, i, int(preliminary_rounds)))
            i += 1


        # Generate and save the new tournament
        tournament = Tournament(random_generator.id(6), password, name, fencers, location, preliminary_rounds, preliminary_groups, first_elimination_round, elimination_mode.lower(), num_pistes)
        save_master_credentials(tournament.id, password)
        tournament_cache.append(tournament)
        save_tournament(tournament)

    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Server Error', 'message': str(e)})

    response = make_response(jsonify({'success': True, 'tournament_id': tournament.id}))
    return create_master_cookie(response, tournament.id)
    


@app.route('/<tournament_id>/check-login')
@app.route('/<tournament_id>/dashboard/check-login')
def check_login(tournament_id):
    """
    Flask processes a GET request to check if the user is logged in.
    """
    if check_logged_in_as_master(request, tournament_id):
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 200

@app.route('/master-login', methods=['POST'])
def master_login():
    """
    Flask processes a POST request to login as a manager.

    Returns
    -------
    redirects to /dashboard/<tournament_id>, 200
        On success
    404
        On tournament not found
    401
        On wrong password
    """
    data = request.get_json()
    tournament_id = data['tournament']
    password = data['password']

    print("Login attempt as master")
    print(tournament_id)

    if not check_tournament_exists(tournament_id):
        print("Tournament not found")
        return jsonify({'error': 'Tournament not found'}), 404
    else:
        tournament = get_tournament(tournament_id)
        print(tournament.password)
        print(password)
        if tournament.password == password:
            response = make_response(redirect(url_for('dashboard', tournament_id=tournament_id)))
            return create_master_cookie(response, tournament_id)
        else:
            return jsonify({'error': 'Wrong password'}), 401


@app.route('/login-fencer', methods=['POST'])
def login_fencer():
    """
    Flask processes a POST request to login as a fencer.
    Note: This is not implemented yet.

    Returns
    -------
    404
    """
    data = request.get_json()
    tournament_id = data['tournament_id']
    search = data['search']

    try: 
        start_number = int(search)
        name = None
    except ValueError:
        start_number = None
        name = search
    

    if not check_tournament_exists(tournament_id):
        print(tournament_id)
        print("Tournament not found")
        return jsonify({'error': 'Tournament not found'}), 404
    else:
        tournament = get_tournament(tournament_id)
        if start_number is None and name is None:
            return jsonify({'error': 'No start number or name given'}), 400
        elif name and name != "":
            fencer_id = tournament.get_fencer_id_by_name(name)
        elif start_number and start_number != "":
            fencer_id = tournament.get_fencer_id_by_start_number(start_number)

        if fencer_id is None:
            return jsonify({'error': 'Fencer not found'}), 404
        else:
            fencer = tournament.get_fencer_by_id(fencer_id)
            response = make_response(jsonify({
            'success': 'Fencer found',
            'tournament_id': tournament_id,
            'fencer_id': fencer.id,
            'description': str(fencer),
            }), 200)
            return create_fencer_cookie(response, tournament_id, fencer.id)


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

    # Check if logged in as referee or master
    if not check_logged_in_as_referee(request, tournament_id) and not check_logged_in_as_master(request, tournament_id):
        return jsonify({"success": False, "message": "User must be logged in as Master or Referee to input results!"}), 401

    green_score = int(request.form['green_score'])
    red_score = int(request.form['red_score'])
    tournament.push_score(match_id, green_score, red_score)
    save_tournament(tournament)
    return jsonify({"success": True}), 200

@app.route('/<tournament_id>/standings')
def standings(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/standings the standings.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    group : str
        The requested group (only if in Preliminary Stage). If ``group`` is "all", overall standings are reported.

    Returns
    standings.html, 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        tournament = get_tournament(tournament_id)
        group = request.args.get('group')
        if group is None:
            group = ""
        return render_template('/dashboard/standings.html', requested_group=group, num_groups=tournament.get_num_groups())

@app.route('/<tournament_id>/standings/update')
def get_standings(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/standings/update the standings of the current state as a json object.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    group : str
        The requested group (only if in Preliminary Stage). If ``group`` is "all", overall standings are reported.

    Returns
    -------
    json object (from tournament.get_standings()
    """
    tournament = get_tournament(tournament_id)
    group = request.args.get('group')

    if tournament is None:
        return jsonify([])

    return jsonify(tournament.get_standings(group=group))

@app.route('/<tournament_id>/standings/fencer/<fencer_id>')
def redirict_fencer_from_standings(tournament_id, fencer_id):
    """
    Flask processes a GET request to redirect to the fencer page from the standings page.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    fencer_id : str
        The id of the fencer.

    Returns
    -------
    302
    """
    return redirect(f'/{tournament_id}/fencer/{fencer_id}')

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
        tournament = get_tournament(tournament_id)
        tournament.next_stage()
        save_tournament(tournament)

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
                tournament_id=tournament.id,
                fencer_id=fencer.id
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
        return jsonify({"success": False})

    logged_in_as_fencer = False
    if check_logged_in_as_fencer(request, tournament_id, fencer_id):
        logged_in_as_fencer = True
        
    return jsonify(tournament.get_fencer_hub_information(fencer_id, logged_in_as_fencer=logged_in_as_fencer))

@app.route('/<tournament_id>/tableau')
def tableau(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/tableau/<round>/<group> the tableau.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    round : str
        The requested round (only if in Preliminary Stage). If ``round`` is "all", overall standings are reported.
    group : str
        The requested group (only if in Preliminary Stage). If ``group`` is "all", overall standings are reported.

    Returns
    -------
    tableau.html, 200
        On success
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return render_template('/tableau.html',
            round=request.args.get('round') if request.args.get('round') is not None else get_tournament(tournament_id).preliminary_stage,
            group=request.args.get('group'),
            tournament_id=tournament_id,
            num_groups=get_tournament(tournament_id).get_num_groups()
            )

@app.route('/<tournament_id>/tableau/update', methods=['GET'])
def get_tableau(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/tableau/<round>/<group>/update the tableau object as a json object.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    round : str
        The requested round (only if in Preliminary Stage). If ``round`` is "all", overall standings are reported.
    group : str
        The requested group (only if in Preliminary Stage). If ``group`` is "all", overall standings are reported.

    Returns
    -------
    json object (from tournament.get_tableau_object()
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify([]), 404
    response = tournament.get_tableau_array(request.args.get('group'))
    return jsonify(response), 200

@app.route('/<tournament_id>/tableau/approve', methods=['POST'])
def approve_tableau(tournament_id):
    """
    Flask processes a POST request to approve the tableau by a certain Fencer.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    round : str
        The requested round (only if in Preliminary Stage). If ``round`` is "all", overall standings are reported.
    group : str
        The requested group (only if in Preliminary Stage). If ``group`` is "all", overall standings are reported.

    Returns
    -------
    200
        On success
    304
        On already approved tableau
    404
        On tournament not found
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        data = request.get_json()
        prelim_round = request.args.get('round')
        if prelim_round is None or prelim_round == (1,):
            prelim_round = get_tournament(tournament_id).preliminary_stage
        group = request.args.get('group')

        # Check if Cookie for logged in fencer exists
        if not check_logged_in_as_fencer(request, tournament_id, data['fencer_id']):
            return jsonify({"success": False, "message": "You are not logged in as the correct fencer."}), 403
        
        # Check if Cookie with device_id exists
        if 'device_id' in request.cookies:
            device_id = request.cookies['device_id']
        else:
            device_id = random_generator.id(16)

        response = make_response(get_tournament(tournament_id).approve_tableau(prelim_round, group, data['timestamp'], data['fencer_id'], device_id), 200)
        
        if 'device_id' not in request.cookies:
            response.set_cookie('device_id', device_id)
        return response

@app.route('/get-my-device-id', methods=['GET'])
def get_my_device_id():
    """
    """
    if 'device_id' in request.cookies:
        return jsonify({"success": True, "device_id": request.cookies['device_id']})
    else:
        return jsonify({"success": False, "message": "No device_id cookie found"})


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

@app.route('/logs/flask')
def get_flask_logs():
    """
    Flask serves on a GET request /logs/flask the flask.log file from the logs folder.
    """
    return send_from_directory('logs', 'flask.log')


@app.route("/server/update")
def update():
    subprocess.call(["sudo", "update.sh"])
    return "Updating..."

@app.route('/server/quit')
def quit():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'



@app.errorhandler(404)
def page_not_found(e):
    """
    404 Error handler: Flask serves on a 404 Error the 404.html file from the templates folder.
    """
    return render_template('404.html'), 404




if __name__ == '__main__':
    load_all_tournaments()
    delete_old_tournaments()


    # ---------- Activate the following boolean to run the server on port 8080 locally ---------- #
    port_flask = False

    # ---------- Activate the following boolean to run the server in debug mode ---------- #
    debug_flask = False


    handler = logging.FileHandler('flask.log')
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    

    if port_flask:
        app.run(host='0.0.0.0', port=8080, debug=debug_flask)
    else:
        app.run(host='0.0.0.0', debug=debug_flask)
    
    