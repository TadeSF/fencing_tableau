import zipfile
from dotenv import load_dotenv
from flask_cors import CORS


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
    import logging.handlers

    import bcrypt
    from flask import (
        Flask,
        Request,
        Response,
        abort,
        jsonify,
        make_response,
        redirect,
        render_template,
        request,
        send_file,
        send_from_directory,
        url_for,
        Markup)
    
    from flask_mail import Mail, Message

    import _version
    import attr_checker
    import random_generator
    from exceptions import *
    from fencer import Fencer, Stage, Wildcard
    from match import EliminationMatch, GroupMatch
    from piste import Piste
    from tournament import *
    import log_parser
    import push_notification

except ModuleNotFoundError:
    raise RequiredLibraryError("Please install all required libraries by running 'pip install -r requirements.txt'")

# ------- Dotenv -------
load_dotenv()
GITHUB_SECRET = os.getenv('GITHUB_SECRET')
MAIL_SENDER = os.getenv('MAIL_SENDER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_ADMIN_RECIPIENTS = os.getenv('MAIL_ADMIN_RECIPIENTS').split(',')
PASSWORD_LOGS = os.getenv('PASSWORD_LOGS')

# ------- Versioning -------
APP_VERSION = _version.VERSION

# ------- Logging -------
try: # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    fh = logging.FileHandler('logs/tournament.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    # Log the start of the server
    logger.info('Server started')
    
except FileNotFoundError:
    pass


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






# ------- Flask / Flask Mail -------
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins="http://localhost:5173")

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)
    print("Running in Gunicorn")
else:
    print("Running in Flask")

app.config['MAIL_SERVER'] = 'smtp.gmx.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# ------- Static Routes -------

# --- Index, Fencer_Login, Favicon ---

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
    # user_agent = request.headers.get("User-Agent")
    # if "mobile" in user_agent.lower() and request.args.get('no_mobile') is None:
    #     return redirect(url_for('mobile_index'))
    return render_template('index.html', version=APP_VERSION)

@app.route('/fencer-login')
def fencer_login():
    """
    Flask serves on GET request / the index.html file from the templates folder.
    """
    return render_template('fencer_login.html', version=APP_VERSION)


# --- Imprint, Privacy, Terms ---

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

@app.route('/terms')
def terms():
    """
    """
    return render_template('terms.html')


# --- Downloads ---

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


# --- Build Your Startlist ---

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


# --- Start-Form ---

@app.route('/get-started')
def get_started():
    """
    Flask serves on GET request /get-started the get_started.html file from the templates folder.
    """
    return render_template('get_started.html')

@app.route('/get-started', methods=['POST'])
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

    name = request.form['name']
    fencers_csv = request.files['fencers']
    location = request.form['location']
    num_pistes = request.form['pistes']
    first_elimination_round = request.form['first_elimination_round']
    elimination_mode = request.form['elimination_mode']
    preliminary_rounds = request.form['number_of_preliminary_rounds']
    preliminary_groups = request.form['number_of_preliminary_groups']
    simulation_active = request.form['simulation_active']
    password = request.form['master_password']
    email = request.form['master_email']
    password = hash_password(password)
    allow_fencers_to_start_matches = request.form['allow_fencers_to_start_matches']
    allow_fencers_to_input_scores = request.form['allow_fencers_to_input_scores']
    allow_fencers_to_referee = request.form['allow_fencers_to_referee']

    # Check if all required fields are filled
    if (
        name == '' or
        fencers_csv.filename == '' or
        num_pistes == '' or
        first_elimination_round == '' or
        elimination_mode == '' or
        preliminary_rounds == '' or
        preliminary_groups == '' or
        password == '' or
        email == ''
    ):
        return jsonify({'success': False, 'error': 'Missing Fields', 'message': 'Please fill out all required fields.'})

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

            fencers.append(Fencer(fencer_name, fencer_club, fencer_nationality,
                           fencer_gender, fencer_handedness, fencer_age, i, int(preliminary_rounds)))
            i += 1

        # Generate and save the new tournament
        tournament = Tournament(
            random_generator.id(6),
            name,
            location,
            email,
            password,

            fencers,

            num_preliminary_rounds=preliminary_rounds,
            num_preliminary_groups=preliminary_groups,
            first_elimination_round=first_elimination_round,
            elimination_mode=elimination_mode.lower(),

            number_of_pistes=num_pistes,

            allow_fencers_to_start_matches=True if allow_fencers_to_start_matches == 'true' else False,
            allow_fencers_to_input_scores=True if allow_fencers_to_input_scores == 'true' else False,
            allow_fencers_to_referee=True if allow_fencers_to_referee == 'true' else False,

            simulation_active=bool(simulation_active == 'true'),
        )
        tournament_cache.append(tournament)

        # Generate Mail
        msg = Message(f'Tournament {tournament.id} created',
                      sender=MAIL_SENDER,
                      recipients=[tournament.master_email])
        msg.html = render_template('email/new_tournament.html',
                                   tournament_id=tournament.id,
                                   tournament_link=f"https://fencewithfriends.online/{tournament.id}/dashboard",
                                   fencer_link=f"https://fencewithfriends.online/fencer-login?tournament={tournament.id}",
                                   tournament_name=tournament.name,
                                   tournament_location=tournament.location,
                                   illustration_number=random.randint(1, 4))
        mail.send(msg)

        save_tournament(tournament)

    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Server Error', 'message': str(e)})

    response = make_response(
        jsonify({'success': True, 'tournament_id': tournament.id}))
    return create_cookie(response, tournament.id, "master")


# --- Web-App-Pages ---

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

@app.route('/qr/fencer')
def fencer_qr():
    """
    Flask serves on GET request /qr the qr.html file from the templates folder.
    This is the page where the QR code is displayed.

    Returns
    -------
    qr.html 200
        On success
    """
    tournament_id = request.args.get('tournament_id')
    return render_template('qr.html', tournament_id=tournament_id)

@app.route('/qr/match')
def match_qr():
    """
    """
    tournament_id = request.args.get('tournament_id')
    match_id = request.args.get('match_id')
    return render_template('qr_match.html', tournament_id=tournament_id, match_id=match_id)

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
    tournament = get_tournament(tournament_id)
    if tournament is None:
        abort(404)
    else:
        group = request.args.get('group')
        if group is None:
            group = ""
        return render_template('/dashboard/standings.html', requested_group=group, num_groups=tournament.get_num_groups(), tournament_id=tournament_id)

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
                               round=request.args.get('round') if request.args.get(
                                   'round') is not None else get_tournament(tournament_id).preliminary_stage,
                               group=request.args.get('group'),
                               tournament_id=tournament_id,
                               num_groups=get_tournament(
                                   tournament_id).get_num_groups()
                               )

@app.route('/<tournament_id>/piste-overview')
def piste_overview(tournament_id):
    """
    """
    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        tournament = get_tournament(tournament_id)
        return render_template('/piste_overview.html', tournament_id=tournament_id, num_pistes=tournament.num_pistes)

@app.route('/<tournament_id>/brackets')
def brackets(tournament_id):
    """
    Flask serves on a GET request /<tournament_id>/brackets the brackets.html file from the templates folder.

    Parameters
    ----------
    tournament_id : str
        The id of the tournament.

    Returns
    -------
    brackets.html, 200
        On success
    404
        On tournament not found
    """

    highlighted_fencer_id = request.args.get('fencer_id')

    if not check_tournament_exists(tournament_id):
        abort(404)
    else:
        return render_template('/brackets.html', tournament_id=tournament_id, highlighted_fencer_id=highlighted_fencer_id if highlighted_fencer_id is not None else 0)

@app.route('/<tournament_id>/<match_id>/live')
@app.route('/live-app')
@app.route('/live-ref')
def live_ref(tournament_id = None, match_id = None):
    if tournament_id:
        try:
            tournament = get_tournament(tournament_id)
            if tournament is None:
                abort(404)

            match = tournament.get_match_by_id(match_id)
            if match is None:
                abort(404)

            fencer_red = match.red.short_str
            fencer_green = match.green.short_str
            fencer_red_id = match.red.id
            fencer_green_id = match.green.id
        except Exception as e:
            logger.error(e)
            abort(404)
    
    else:
        fencer_red = "Red"
        fencer_green = "Green"
        fencer_red_id = ""
        fencer_green_id = ""

    return render_template('/live_ref.html', tournament_id=tournament_id, match_id=match_id, fencer_red=fencer_red, fencer_green=fencer_green, fencer_red_id=fencer_red_id, fencer_green_id=fencer_green_id)


# --- Login-Methods ---

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
            response = make_response(
                redirect(url_for('dashboard', tournament_id=tournament_id)))
            return create_cookie(response, tournament_id, "master")
        else:
            return jsonify({'error': 'Wrong password'}), 401


@app.route('/<tournament_id>/check-login')
@app.route('/<tournament_id>/dashboard/check-login')
def check_login(tournament_id):
    """
    Flask processes a GET request to check if the user is logged in.
    """
    if check_logged_in(request, tournament_id, "master"):
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 200

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



# ------- API --------

# --- Error Responses ---
def default_error(e: Exception = None, traceback = None, code = "DEFAULT_ERROR", message = "An error occured"):
    response = {"error": {'code': code, 'message': message}}
    if e is not None:
        response["error"]["exception"] = str(e)
    if traceback is not None:
        response["error"]["traceback"] = traceback

    return jsonify(response)

def tournament_not_found_error():
    return default_error(code = "TOURNAMENT_NOT_FOUND", message = "Tournament not found")

# --- Dashboard ---

# @app.route('/<tournament_id>/dashboard/update', methods=['GET'])
@app.route('/api/dashboard/update', methods=['GET']) # BEARBEITET
def get_dashboard_infos():
    """
    """
    tournament_id = request.args.get('tournament_id')
    tournament = get_tournament(tournament_id)
    if tournament is None:
        return tournament_not_found_error(), 404
    return jsonify(tournament.get_dashboard_infos())


# --- Matches ---

# @app.route('/<tournament_id>/matches/update', methods=['GET'])
@app.route('/api/matches/update', methods=['GET']) # BEARBEITET
def get_matches():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error(), 404
        return jsonify(tournament.get_matches())
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e)

# @app.route('/<tournament_id>/matches/set_active', methods=['POST'])
@app.route('/api/matches/set-active', methods=['POST']) # BEARBEITET
def set_active():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        match_id = request.args.get('match_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error(), 404
        
        if "live_ref" in request.json:
            live_ref = request.json['live_ref']
            logger.info(f"Started match {match_id} with live ref")
        else:
            live_ref = False
        
        # Check if logged in as referee or master
        if not check_logged_in(request, tournament_id, "referee") and not check_logged_in(request, tournament_id, 'master') and not tournament.allow_fencers_to_start_matches and not live_ref:
            return default_error(code = "NOT_LOGGED_IN", message = "User must be logged in to input Results!"), 401
        
        override_flag = request.json['override_flag']

        tournament.set_active(match_id, override_flag)
        save_tournament(tournament)
        return {}, 200
    
    except OccupiedPisteError:
        return default_error(code = "PISTE_OCCUPIED", message = "Piste is already in use by another match."), 400
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500
        
# @app.route('/<tournament_id>/matches/push_score', methods=['POST'])
@app.route('/api/matches/push-score', methods=['POST']) # BEARBEITET
def push_score():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        match_id = request.args.get('match_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error(), 404
        
        if "live_ref" in request.json:
            live_ref = request.json['live_ref']
            logger.info(f"Finished match {match_id} with live ref")
        else:
            live_ref = False
        

        # Check if logged in as referee or master
        
        if not check_logged_in(request, tournament_id, "referee") and not check_logged_in(request, tournament_id, 'master') and not tournament.allow_fencers_to_input_scores and not live_ref:
            return default_error(code = "NOT_LOGGED_IN", message = "User must be logged in to input Results!"), 401

        green_score = int(request.json['green_score'])
        red_score = int(request.json['red_score'])

        tournament.push_score(match_id, green_score, red_score)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc())

# @app.route('/<tournament_id>/matches/prioritize', methods=['POST'])
@app.route('/api/matches/prioritize', methods=['POST']) # BEARBEITET
def prioritize():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        match_id = request.args.get('match_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        value = request.json['value']

        tournament.prioritize_match(match_id, value)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/matches/assign_piste', methods=['POST'])
@app.route('/api/matches/assign-piste', methods=['POST']) # BEARBEITET
def assign_piste():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        match_id = request.args.get('match_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        piste = int(request.json['piste'])

        tournament.assign_certain_piste(match_id, piste)
        save_tournament(tournament)
        return {}, 200

    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/matches/remove_piste_assignment', methods=['POST'])
@app.route('/api/matches/remove-piste-assignment', methods=['POST']) # BEARBEITET
def remove_piste_assignment():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        match_id = request.args.get('match_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        tournament.remove_piste_assignment(match_id)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/matches-left', methods=['GET'])


@app.route('/api/matches/matches-left', methods=['GET']) # BEARBEITET
def matches_left():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        return jsonify({"matches_left": tournament.get_matches_left()}), 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


# --- Standings ---

# @app.route('/<tournament_id>/standings/update')
@app.route('/api/standings/update', methods=['GET']) # BEARBEITET
def get_standings():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        group = request.args.get('group')
        gender = request.args.get('gender')
        handedness = request.args.get('handedness')
        age_group = request.args.get('age')

        return jsonify(tournament.get_standings(group, gender, handedness, age_group)), 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


# --- Master Requests ---

# @app.route('/<tournament_id>/next-stage')
@app.route('/api/next-stage', methods=['GET']) # BEARBEITET
def next_stage():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        tournament.next_stage()
        save_tournament(tournament)

        # Send all results to master via Email
        if tournament.stage == Stage.FINISHED:
            msg = Message(f'Tournament {tournament.id} Results',
                        sender=MAIL_SENDER,
                        recipients=[tournament.master_email])

            attached_files_string = os.listdir(f'results/{tournament.id}')
            attached_files_string.sort()
            attached_files_string = Markup("<br>".join(attached_files_string))

            msg.html = render_template('email/result_mail.html',
                                        tournament_id=tournament.id,
                                        tournament_name=tournament.name,
                                        tournament_location=tournament.location,
                                        winner=tournament.get_winner().name,
                                        attached_files=attached_files_string,
                                        illustration_number=random.randint(1, 4))

            for result in os.listdir(f'results/{tournament.id}'):
                with open(f'results/{tournament.id}/{result}', 'rb') as f:
                    msg.attach(result, 'application/csv', f.read())

            mail.send(msg)

        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/download-results')
@app.route('/api/download-results', methods=['GET']) # BEARBEITET
def download_results():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        # Create a zip file
        zip_file = zipfile.ZipFile(f'results/{tournament.id}.zip', 'w')
        for result in os.listdir(f'results/{tournament.id}'):
            zip_file.write(f'results/{tournament.id}/{result}', result)
        zip_file.close()

        return send_file(f'results/{tournament.id}.zip', as_attachment=True)
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


# --- Piste ---

# @app.route('/<tournament_id>/piste-overview/get-status')
@app.route('/api/piste/update', methods=['GET']) # BEARBEITET
def piste_overview_update():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        piste = request.args.get('piste')

        tournament = get_tournament(tournament_id)
        return jsonify(tournament.get_piste_status(piste))
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/piste-overview/toggle-piste', methods=['POST'])
@app.route('/api/piste/toggle', methods=['POST']) # BEARBEITET
def toggle_piste():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        piste = int(request.args.get('piste'))

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        tournament.toggle_piste(piste)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc())


# --- Fencer ---

# @app.route('/<tournament_id>/fencer/<fencer_id>/update', methods=['GET'])
@app.route('/api/fencer/update', methods=['GET']) # BEARBEITET
def get_fencer():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        fencer_id = request.args.get('fencer_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        logged_in_as_fencer = check_logged_in(request, tournament_id, 'fencer', fencer_id)
        logged_in_as_master = check_logged_in(request, tournament_id, 'master')
        
        fencer_hub_information = tournament.get_fencer_hub_information(fencer_id)
        fencer_hub_information['logged_in_as_fencer'] = logged_in_as_fencer
        fencer_hub_information['logged_in_as_master'] = logged_in_as_master

        return jsonify(fencer_hub_information)
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/fencer/<fencer_id>/change_attribute', methods=['POST'])
@app.route('/api/fencer/change-attribute', methods=['POST']) # BEARBEITET
def change_fencer_attribute():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        fencer_id = request.args.get('fencer_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        logged_in_as_fencer = check_logged_in(request, tournament_id, 'fencer', fencer_id)
        logged_in_as_master = check_logged_in(request, tournament_id, 'master')

        if not logged_in_as_fencer and not logged_in_as_master:
            return default_error(code="NOT_LOGGED_IN", message='Client is not logged in. As Master or corresponding Fencer'), 401


        attribute = request.json['attribute']
        value = request.json['value']

        if attribute not in ["name", "club", "nationality", "gender", "handedness", "age"]:
            return default_error(code="INVALID_ATTRIBUTE_NAME", message='Client provided an invalid attribute name. Attribute name must be one of these: ["name", "club", "nationality", "gender", "handedness", "age"]'), 400
        
        if value is None:
            return default_error(code="INVALID_ATTRIBUTE_VALUE", message='Client provided an invalid attribute value. Attribute value must not be None.'), 400
    
        tournament.get_fencer_by_id(fencer_id).change_attribute(attribute, value)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

# @app.route('/<tournament_id>/tableau/approve', methods=['POST'])
@app.route('/api/fencer/approve-tableau', methods=['POST']) # BEARBEITET
def approve_tableau():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        fencer_id = request.args.get('fencer_id')
        group = request.args.get('group')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        data = request.get_json()
        prelim_round = request.args.get('round')
        if prelim_round is None or prelim_round == (1,): # TODO Bugfix this
            prelim_round = get_tournament(tournament_id).preliminary_stage

        # Check if Cookie for logged in fencer exists
        if not check_logged_in(request, tournament_id, "fencer", fencer_id):
            return default_error(code="NOT_LOGGED_IN", message="Client is not logged in as fencer"), 401

        # Check if Cookie with device_id exists
        if 'device_id' in request.cookies:
            device_id = request.cookies['device_id']
        else:
            device_id = random_generator.id(16)

        response = make_response(get_tournament(tournament_id).approve_tableau(
            prelim_round, group, data['timestamp'], fencer_id, device_id), 200)

        if 'device_id' not in request.cookies:
            response.set_cookie('device_id', device_id)
        return response
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500
    
@app.route('/api/fencer/disqualify', methods=['GET'])
def get_disqualify_fencer_information():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        start_number = request.args.get('start_number')
        if start_number is not None:
            start_number = int(start_number)
        name_query = request.args.get('name')

        print(name_query)

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error(), 404
        
        # Check if logged in as master
        if not check_logged_in(request, tournament_id, "master"):
            return default_error(code="NOT_LOGGED_IN", message="Client is not logged in as master"), 401
        
        if start_number:
            fencer = tournament.get_fencer_by_start_number(start_number)
        elif name_query:
            fencer = tournament.get_fencer_by_name(name_query)
        else:
            return default_error(code="INVALID_ARGUMENTS", message="Client provided invalid arguments"), 400

        if fencer is None:
            return default_error(code="FENCER_NOT_FOUND", message="Fencer with start number {} not found".format(start_number)), 404
        
        response = {
            "id": fencer.id,
            "name": fencer.name,
            "start_number": fencer.start_number,
            "club": fencer.club,
            "nationality": fencer.nationality,
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


@app.route('/api/fencer/disqualify', methods=['POST'])
def disqualify_fencer():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        fencer_id = request.args.get('fencer_id')

        data = request.get_json()
        
        reason = data['reason']

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error(), 404
        
        # Check if logged in as master
        # if not check_logged_in(request, tournament_id, "master"):
        #     return default_error(code="NOT_LOGGED_IN", message="Client is not logged in as master"), 401
        
        tournament.disqualify_fencer(fencer_id, reason)
        save_tournament(tournament)

        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500



# --- Tableau ---

# @app.route('/<tournament_id>/tableau/update', methods=['GET'])
@app.route('/api/tableau/update', methods=['GET']) # BEARBEITET
def get_tableau():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        group = request.args.get('group')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        response = tournament.get_tableau_array(group)
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500
    

# --- Brackets ---

@app.route('/api/brackets/update', methods=['GET'])
def get_brackets():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        response = tournament.elimination_brackets[0].map()
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc())
    

# --- Push Notifications ---
@app.route('/api/push/subscribe', methods=['POST'])
def subscribe_push():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        fencer_id = request.args.get('fencer_id')

        data = request.get_json()
        tournament.get_fencer_by_id(fencer_id).subscribe_to_push_notifications(data['token'])
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500

@app.route('/api/push/unsubscribe', methods=['POST'])
def unsubscribe_push():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        fencer_id = request.args.get('fencer_id')

        data = request.get_json()
        token = data['token']

        tournament.get_fencer_by_id(fencer_id).unsubscribe_from_push_notifications(token)
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


# --- Helpers ---

# @app.route('/<tournament_id>/simulate-current')
@app.route('/api/simulate', methods=['GET']) # BEARBEITET
def simulate():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')

        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()

        tournament.simulate_current()
        save_tournament(tournament)
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


# ------- Docs -------

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




# ------- Logs and Utility -------

@app.route('/github-webhook', methods=['POST'])
def handle_webhook():
    """
    """
    # # Verify the signature
    # signature = request.headers.get('X-Hub-Signature-256')
    # if not signature:
    #     return 'No signature found', 400
    # try:
    #     algorithm, signature = signature.split('=')
    #     if algorithm != 'sha256':
    #         raise ValueError
    # except ValueError:
    #     return 'Invalid algorithm', 400
    # mac = hmac.new(github_secret.encode(), msg=request.data, digestmod=hashlib.sha256)
    # if not hmac.compare_digest(mac.hexdigest(), signature):
    #     return 'Invalid signature', 400

    msg = Message("GitHub Webhook",
                  sender=MAIL_SENDER,
                  recipients=MAIL_ADMIN_RECIPIENTS)

    msg.html = render_template('/email/github_webhook.html')
    mail.send(msg)

    # try:
    #     # Execute the update script
    #     subprocess.call(['/usr/bin/bash', '/home/pi/fencing_tableau/update_server.sh'])
    # except Exception as e:
    #     return 'Error: {}'.format(e), 500

    return 'Webhook received', 200

@app.route('/webhook/notification_test', methods=['POST'])
def webhook_notification_test():
    """
    """
    try:
        tournament_id = request.args.get('tournament_id')
        tournament = get_tournament(tournament_id)
        if tournament is None:
            return tournament_not_found_error()
        
        fencer_id = request.args.get('fencer_id')

        fencer = tournament.get_fencer_by_id(fencer_id)
        push_notification.send_fencer_push_message(fencer, 'This is a test notification.')
        return {}, 200
    
    except Exception as e:
        logger.error(e, exc_info=True)
        return default_error(e, traceback.format_exc()), 500


@app.route('/logs')
def logs():
    """
    Flask renders on a GET request /logs the logs.html template.
    """
    return render_template('logs.html')

@app.route('/logs/get', methods=['POST'])
def get_logs():
    """
    Flask processes a POST request to get the logs from the server.
    """
    try:
        password = request.json['password']
        cookie = request.cookies.get('logs_cookie')
        
        if cookie != None:
            try:
                with open('logs/cookies.txt', 'r') as f:
                    cookies = f.read().splitlines()
            except Exception as e:
                logger.error('Exception: %s', e, exc_info=True)
                
            if cookie in cookies:
                tournament_logs = log_parser.parse_tournament_log()
                logger.info('Logs accessed')
                return jsonify({"success": True, "tournament_logs": tournament_logs}), 200
        

        if password != None:
            if check_password(password, PASSWORD_LOGS):
                tournament_logs = log_parser.parse_tournament_log()
                logger.info('Logs accessed')
                cookie = random_generator.cookie()
                response = make_response(jsonify({"success": True, "tournament_logs": tournament_logs}), 200)
                response.set_cookie('logs_cookie', cookie)
                with open('logs/cookies.txt', 'a') as f:
                    f.write(cookie + '\n')
                return response
            else:
                logger.info('Wrong password for logs')
                return jsonify({'error': 'Wrong password'}), 401
            
        return jsonify({'error': 'No password or cookie'}), 401
        
    except Exception as e:
        # Log the error and traceback
        logger.error('Exception: %s', e, exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500



# ------- Error handlers -------
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
@app.errorhandler(408)
@app.errorhandler(409)
@app.errorhandler(410)
@app.errorhandler(500)
@app.errorhandler(501)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
@app.errorhandler(505)
def page_not_found(e):
    """
    """
    return render_template('error.html', error=e.code, explain=e), e.code


# ------- Testing locally -------
if __name__ == '__main__':
    load_all_tournaments()
    delete_old_tournaments()


    # ---------- Activate the following boolean to run the server on port 8080 locally ---------- #
    port_flask = True

    # ---------- Activate the following boolean to run the server in debug mode ---------- #
    debug_flask = True


    if port_flask:
        app.run(host='0.0.0.0', port=8080, debug=debug_flask)
    else:
        app.run(host='0.0.0.0', debug=debug_flask)
