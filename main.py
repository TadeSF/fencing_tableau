from dotenv import load_dotenv


try:
    import csv
    import datetime
    import hashlib
    import hmac
    import logging
    import os
    import pickle
    import subprocess
    import threading
    import traceback
    from typing import List, Literal

    import bcrypt
    from flask import (Flask, Request, Response, abort, jsonify, make_response,
                       redirect, render_template, request, send_file,
                       send_from_directory, url_for)

    import _version
    import attr_checker
    import random_generator
    from exceptions import *
    from fencer import Fencer, Stage, Wildcard
    from match import EliminationMatch, GroupMatch
    from piste import Piste
    from tournament import *

except ModuleNotFoundError:
    raise RequiredLibraryError("Please install all required libraries by running 'pip install -r requirements.txt'")

# ------- Dotenv -------
load_dotenv()
github_secret = os.getenv('GITHUB_SECRET')

# ------- Versioning -------
APP_VERSION = _version.VERSION


# ------- Tournament Cache -------
enable_tournament_cache = False

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
    global tournament_cache, cache_lock, enable_tournament_cache

    if enable_tournament_cache:
        with cache_lock:
            for tournament in tournament_cache:
                if tournament.id == tournament_id:
                    return tournament
            return None
    else:
        return load_tournament(tournament_id)


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
    global tournament_cache, cache_lock, enable_tournament_cache

    if enable_tournament_cache:
        with cache_lock:
            for tournament in tournament_cache:
                if tournament.id == tournament_id:
                    return True
            return False
    else:
        return os.path.exists(f'tournament_cache/{tournament_id}.pickle')


# ------- Pickeling -------
# Pickeling is an easy way to save data to a file, so that it stays persistent even if the server has to restart.



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

def load_tournament(tournament_id: str) -> Tournament:
    """
    This function loads a tournament from a file, given an id.
    This is done by pickeling a tournament object. The file is saved in the /tournaments folder and is named after the tournament id.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament to be loaded.

    Returns
    -------
    Tournament object
        if the tournament exists
    None
        if the tournament does not exist
    """
    create_local_tournament_folder()
    if os.path.exists(f'tournament_cache/{tournament_id}.pickle'):
        with open(f'tournament_cache/{tournament_id}.pickle', 'rb') as f:
            tournament = pickle.load(f)
            return tournament
    else:
        return None

def load_all_tournaments(return_values: bool = False):
    """
    This function loads all saved tournaments from the /tournaments folder and adds them to the tournament cache.
    """
    global tournament_cache, cache_lock
    tournaments = []
    with cache_lock:
        create_local_tournament_folder()
        for file in os.listdir('tournament_cache'):
            if file.endswith('.pickle'):
                with open(f'tournament_cache/{file}', 'rb') as f:
                    tournament = pickle.load(f)
                    if tournament is not None:
                        tournaments.append(tournament)
    if return_values:
        return tournaments
    else:
        tournament_cache = tournaments


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



# ------- Login-Cookies -------
def create_cookie(response: Response, tournament_id: str, clearence: Literal["master", "referee", "fencer"], fencer_id: str = None) -> Response:
    """
    """
    cookie_value = random_generator.cookie()
    tournament = get_tournament(tournament_id)

    if clearence == "master":
        tournament.master_cookies.append(cookie_value)
        response.set_cookie(tournament_id + "_master", cookie_value, max_age=60*60*24*7) # 7 days
    if clearence == "referee":
        tournament.referee_cookies.append(cookie_value)
        response.set_cookie(tournament_id + "_referee", cookie_value, max_age=60*60*24*7) # 7 days
    if clearence == "fencer":
        tournament.get_fencer_by_id(fencer_id).cookies.append(cookie_value)
        response.set_cookie(tournament_id + "_fencer_" + fencer_id, cookie_value, max_age=60*60*24*7) # 7 days

    save_tournament(tournament)
    print(f"Created {clearence} cookie for tournament {tournament_id} with value {cookie_value}")
    return response

def check_logged_in(request: Request, tournament_id: str, clearence: Literal["master", "referee", "fencer"], fencer_id: str = None) -> bool:
    """
    """
    if clearence == "master" or clearence == "referee":
        for cookie_name, cookie_value in request.cookies.items():
            if cookie_name == f"{tournament_id}_{clearence}":
                if cookie_value in getattr(get_tournament(tournament_id), clearence + "_cookies"):
                    print(f"Found {clearence} cookie for tournament {tournament_id} with value {cookie_value}")
                    return True
    
    elif clearence == "fencer":
        for cookie_name, cookie_value in request.cookies.items():
            if cookie_name == f"{tournament_id}_{clearence}_{fencer_id}":
                if cookie_value in get_tournament(tournament_id).get_fencer_by_id(fencer_id).cookies:
                    print(f"Found {clearence} cookie for tournament {tournament_id} with value {cookie_value}")
                    return True

    print(f"Did not find {clearence} cookie for tournament {tournament_id}")
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
    """
    This function checks if a csv file is valid and returns a list of fencers.

    Parameters
    ----------
    file : csv file
        The csv file to be checked.

    Returns
    -------
    list of Fencer objects
        if the csv file is valid
    None
        if the csv file is not valid

    Raises
    ------
    CSVError
        if the csv file is not valid and provides a description of the error
    """
    headers = next(file)
    body = []
    if headers != ['Name', 'Club', 'Nationality', 'Gender', 'Handedness', 'Age']:
        print(headers)
        raise CSVError(f"Invalid headers\n\nMust be {['Name', 'Club', 'Nationality', 'Gender', 'Handedness', 'Age']}")

    row_number = 0
    for row in file:
        row_number += 1

        if len(row) != 6:
            raise CSVError(f"Invalid number of columns in row {row_number}")
        name, club, nationality, gender, handedness, age = row

        try:
            attr_checker.check_name(name)
            attr_checker.check_club(club)
            attr_checker.check_nationality(nationality)
            attr_checker.check_gender(gender)
            attr_checker.check_handedness(handedness)
            age = attr_checker.check_age(age)
        except Exception as e:
            raise CSVError(f"Invalid attribute in row {row_number}: {e}")
        
        body.append([name, club, nationality, gender, handedness, age])

    if len(body) < 3:
        raise CSVError(f"CSV file does not contain enough (or any) fencers. Please add at least 3 fencers.")
    
    return body

# ------- Passwords -------
def hash_password(password: str) -> str:
    """
    This function hashes a password using the bcrypt algorithm.

    Parameters
    ----------
    password : str
        The password to be hashed.

    Returns
    -------
    str
        The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    This function checks if a password matches a hashed password.

    Parameters
    ----------
    password : str
        The password to be checked.
    hashed_password : str
        The hashed password to be checked against.

    Returns
    -------
    bool
        True if the password matches the hashed password.
        False if the password does not match the hashed password.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


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
    user_agent = request.headers.get("User-Agent")
    if "mobile" in user_agent.lower():
        return redirect(url_for('mobile_index'))
    return render_template('index.html', version=APP_VERSION)

@app.route('/m')
def mobile_index():
    """
    Flask serves on GET request / the index.html file from the templates folder.
    """
    return render_template('m_index.html', version=APP_VERSION)

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

@app.route('/example-startlist')
def example_startlist_download():
    """
    """
    try:
        return send_file("static/example_startlist.csv", as_attachment=True)
    except Exception as e:
        return str(e)

@app.route('/build-your-startlist')
def build_your_startlist():
    """
    """
    startlist_id = request.args.get("id")
    if startlist_id is None:
        startlist_id = random_generator.id(20)
        return redirect(url_for('build_your_startlist', id=startlist_id))

    if not os.path.exists("build_your_startlist"):
        os.mkdir("build_your_startlist")
        print("Created build_your_startlist folder")

    if not os.path.exists(f"build_your_startlist/{startlist_id}.csv"):
        with open(f"build_your_startlist/{startlist_id}.csv", "w") as f:
            f.write("Name,Club,Nationality,Gender,Handedness,Age")

    return render_template('build_your_startlist.html', version=APP_VERSION, startlist_id=startlist_id)

@app.route('/build-your-startlist/get-startlist', methods=['GET'])
def get_startlist():
    """
    """
    startlist_id = request.args.get("id")

    # try:
    with open(f"build_your_startlist/{startlist_id}.csv", "r") as f:
        data = csv.reader(f)
        next(data)
        return {"success": True, "startlist": [line for line in data]}

    # except Exception as e:
    #     return {"success": False, "message": str(e)}


@app.route('/build-your-startlist/add-fencer', methods=['POST'])
def add_fencer():
    """
    """
    startlist_id = request.json.get("startlist_id")
    name = request.json.get("name")
    club = request.json.get("club")
    nationality = request.json.get("nationality")
    gender = request.json.get("gender")
    handedness = request.json.get("handedness")
    age = request.json.get("age")

    try:
        with open(f"build_your_startlist/{startlist_id}.csv", "a") as f:
            f.write(f"\n{name},{club},{nationality},{gender},{handedness},{age}")
            return {"success": True}

    except Exception as e:
        return {"success": False, "message": str(e)}


@app.route('/build-your-startlist/delete-fencer', methods=['POST'])
def delete_fencer():
    """
    """
    startlist_id = request.json.get("startlist_id")
    row_number = request.json.get("row_number")

    try:
        with open(f"build_your_startlist/{startlist_id}.csv", "r") as f:
            data = csv.reader(f)
            lines = [",".join(line) + "\n" for line in data]
            lines.pop(int(row_number))
            # remove the last "\n"
            lines[-1] = lines[-1][:-1]
        with open(f"build_your_startlist/{startlist_id}.csv", "w") as f:
            f.writelines(lines)
            return {"success": True}

    except Exception as e:
        return {"success": False, "message": str(e)}



@app.route('/build-your-startlist/save-startlist', methods=['GET'])
def save_startlist():
    """
    This function is responsible for saving a startlist, which is a list of fencers and their corresponding bout numbers, to a CSV file.
    The function is called when the user clicks the button to save a startlist. The function takes the ID of the startlist as an argument
    and then creates a CSV file by calling the send_file() function. The file is named fencing_startlist_{startlist_id}.csv and is 
    automatically downloaded by the user's browser.
    """
    startlist_id = request.args.get("id")
    try:
        return send_file(f"build_your_startlist/{startlist_id}.csv", as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/tournaments')
def tournaments():
    """
    Flask serves on GET request /tournaments the tournaments.html file from the templates folder.
    """

    cards = []
    i = 0
    for tournament in load_all_tournaments(return_values=True):
        i += 1
        tournament_id = tournament.id
        tournament_id_with_parenthesies = f"'{tournament_id}'"
        name = tournament.name
        date = tournament.created_at.strftime("%d.%m.%Y %H:%M")
        cards.append(f'<div class="grid-item"><div class="ID-Block"><div class="ID-Block-Number">{tournament_id}</div><div class="ID-Block-Description">Tournament ID</div></div><div class="Name">{name}</div><div class="date">{date}</div><div class="button-box"><div class="button" onclick="ManageTournament({tournament_id_with_parenthesies})">Manage Tournament</div><div class="button" onclick="LoginAsFencer({tournament_id_with_parenthesies})">Login as Fencer</div></div></div>')

    if i == 0:
        cards.append('<div class="grid-item" style="grid-column: span 3;"><div class="Name">No Tournaments</div></div>')
    return render_template('tournaments.html', cards=''.join(cards))

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
    simulation_active = request.form['simulation_active']
    print(simulation_active)
    print(bool(simulation_active == 'true'))
    password = request.form['master_password']
    password = hash_password(password)

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
        tournament = Tournament(random_generator.id(6), password, name, fencers, location, preliminary_rounds, preliminary_groups, first_elimination_round, elimination_mode.lower(), num_pistes, bool(simulation_active == 'true'))
        tournament_cache.append(tournament)
        save_tournament(tournament)

    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Server Error', 'message': str(e)})

    response = make_response(jsonify({'success': True, 'tournament_id': tournament.id}))
    return create_cookie(response, tournament.id, "master")
    


@app.route('/<tournament_id>/check-login')
@app.route('/<tournament_id>/dashboard/check-login')
def check_login(tournament_id):
    """
    Flask processes a GET request to check if the user is logged in.
    """
    if check_logged_in(request, tournament_id, "master"):
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
        if check_password(password, tournament.password):
            response = make_response(redirect(url_for('dashboard', tournament_id=tournament_id)))
            return create_cookie(response, tournament_id, "master")
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
            return create_cookie(response, tournament_id, "fencer", fencer_id=fencer.id)

@app.route('/<tournament_id>/check-fencer-login')
def check_fencer_login(tournament_id):
    """
    Flask processes a GET request to check if the user is logged in.
    """
    fencer_id = request.args.get('fencer_id')
    if check_logged_in(request, tournament_id, "fencer", fencer_id=fencer_id):
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 200



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
        abort(500)
    else:
        return render_template('dashboard.html', tournament_id=tournament_id)

@app.route('/qr')
def qr():
    """
    Flask serves on GET request /qr the qr.html file from the templates folder.
    This is the page where the QR code is displayed.

    Returns
    -------
    qr.html 200
        On success
    """
    tournament_id = request.args.get('tournament')
    return render_template('qr.html', tournament_id=tournament_id)

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
        return render_template('/dashboard/matches.html', tournament_id=tournament_id, num_pistes=get_tournament(tournament_id).num_pistes)

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
    if not check_logged_in(request, tournament_id, "referee") and not check_logged_in(request, tournament_id, 'master'):
        return jsonify({"success": False, "message": "User must be logged in as Master or Referee to input results!"}), 401

    green_score = int(request.form['green_score'])
    red_score = int(request.form['red_score'])
    tournament.push_score(match_id, green_score, red_score)
    save_tournament(tournament)
    return jsonify({"success": True}), 200

@app.route('/<tournament_id>/matches/prioritize', methods=['POST'])
def prioritize(tournament_id):
    """
    Flask processes a POST request to prioritize a match in the piste-assignment-process.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    match_id : str
        The id of the match.
    
    Returns
    -------
    200
    """
    tournament = get_tournament(tournament_id)
    match_id = request.json['id']
    value = request.json['value']
    tournament.prioritize_match(match_id, value)
    save_tournament(tournament)
    return jsonify({"success": True}), 200

@app.route('/<tournament_id>/matches/assign_piste', methods=['POST'])
def assign_piste(tournament_id):
    """
    Flask processes a POST request to assign a piste to a match.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    match_id : str
        The id of the match.
    piste : int
        The number of the piste.
    
    Returns
    -------
    200
    """
    try:
        tournament = get_tournament(tournament_id)
        match_id = request.json['id']
        piste = int(request.json['piste'])
        tournament.assign_certain_piste(match_id, piste)
        save_tournament(tournament)
        return jsonify({"success": True}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": {e}}), 400

@app.route('/<tournament_id>/matches/remove_piste_assignment', methods=['POST'])
def remove_piste_assignment(tournament_id):
    """
    Flask processes a POST request to remove a piste assignment from a match.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.
    match_id : str
        The id of the match.
    
    Returns
    -------
    200
    """
    try:
        tournament = get_tournament(tournament_id)
        match_id = request.json['id']
        tournament.remove_piste_assignment(match_id)
        save_tournament(tournament)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400



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
        return render_template('/dashboard/standings.html', requested_group=group, num_groups=tournament.get_num_groups(), tournament_id=tournament_id)

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
    gender = request.args.get('gender')
    handedness = request.args.get('handedness')
    age_group = request.args.get('age')


    if tournament is None:
        return jsonify([])

    return jsonify(tournament.get_standings(group, gender, handedness, age_group))

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
                fencer_id=fencer.id,
                version=APP_VERSION
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
        
    return jsonify(tournament.get_fencer_hub_information(fencer_id))

@app.route('/<tournament_id>/fencer/<fencer_id>/change_attribute', methods=['POST'])
def change_fencer_attribute(tournament_id, fencer_id):
    """
    """
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return jsonify({"success": False})
    
    # TODO Check if logged in as fencer or manager

    attribute = request.json.get('attribute')

    if attribute not in ["name", "club", "nationality", "gender", "handedness", "age"]:
        return jsonify({"success": False, "message": "Invalid attribute name"})
    
    value = request.json.get('value')
    if value is None:
        return jsonify({"success": False, "message": "Invalid value"})
    
    try:
        tournament.get_fencer_by_id(fencer_id).change_attribute(attribute, value)
        save_tournament(tournament)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    


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
        if not check_logged_in(request, tournament_id, "fencer", data['fencer_id']):
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
        tournament = get_tournament(tournament_id)
        tournament.simulate_current()
        save_tournament(tournament)
        return '', 200


@app.route('/docs/<path:filename>')
def serve_docs(filename):
    """
    Flask serves and renders on a GET request /docs/build/index.html file from the docs folder. This is the documentation.
    The documentation is built using Sphinx. See the docs folder for more information.
    The template is based on the Read the Docs theme.
    
    The template is not in the templates folder, the path has to be specified manually.
    """
    # If the file does not have an extension, add .html
    if '.' not in filename:
        filename += '.html'
    return send_from_directory('docs/build', filename)
    

@app.route('/docs')
def redirect_docs():
    """
    Flask redirects on a GET request /docs to /docs/build/index.html.
    """
    return redirect(url_for('serve_docs', filename='index.html'))


@app.route('/logs/flask')
def get_flask_logs():
    """
    Flask serves on a GET request /logs/flask the flask.log file from the logs folder.
    """
    return send_from_directory('logs', 'flask.log')


@app.route('/github-webhook', methods=['POST'])
def handle_webhook():

    # Verify the signature
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        return 'No signature found', 400
    try:
        algorithm, signature = signature.split('=')
        if algorithm != 'sha1':
            raise ValueError
    except ValueError:
        return 'Invalid signature', 400
    mac = hmac.new(github_secret.encode(), msg=request.data, digestmod=hashlib.sha1)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return 'Invalid signature', 400

    # Pull the latest changes
    subprocess.run(['sudo', 'update_server.sh'])

    return 'Webhook received', 200



@app.errorhandler(404)
def page_not_found(e):
    """
    404 Error handler: Flask serves on a 404 Error the 404.html file from the templates folder.
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    500 Error handler: Flask serves on a 500 Error the 500.html file from the templates folder.
    """
    return render_template('500.html'), 500


# ------- Flask Mail -------




# ------- Testing locally -------
if __name__ == '__main__':
    load_all_tournaments()
    delete_old_tournaments()


    # ---------- Activate the following boolean to run the server on port 8080 locally ---------- #
    port_flask = True

    # ---------- Activate the following boolean to run the server in debug mode ---------- #
    debug_flask = True


    handler = logging.FileHandler('flask.log')
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    if port_flask:
        app.run(host='0.0.0.0', port=8080, debug=debug_flask)
    else:
        app.run(host='0.0.0.0', debug=debug_flask)