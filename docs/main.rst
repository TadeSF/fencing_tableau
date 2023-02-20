Main
====

This module is the main module of the application. It contains the main functions as well as the Flask server setup and routes.


Tournament Cache
----------------
The Tournament Cache is a list of all the tournaments that are currently loaded in the application. It is used to have the tournament ready in RAM for quicker loading times and to avoid loading the same tournament twice.

.. autofunction:: main.get_tournament

.. autofunction:: main.check_tournament_exists


Tournament Loading/Saving
-------------------------
These Functions are used to load and save tournaments from the /tournaments directory, where they get saved in case the server crashes.

.. autofunction:: main.save_tournament

.. autofunction:: main.load_all_tournaments

.. autofunction:: main.delete_old_tournaments


Flask Server Setup
------------------
If the main.py file is executed directly, Flask will start the server. The server is configured to run on the local network, so that it can be accessed from other devices on the same network. In adittion, the Tournament Cache is filled with loaded files as mentioned above.
The server will be run on port 8080::
   # Setting up the Flask server
   app = Flask(__name__, static_folder='static', template_folder='templates')


   if __name__ == '__main__':

      # Load all tournaments from the /tournaments directory and delete old tournaments
      load_all_tournaments()
      delete_old_tournaments()

      # Start the server on port 8080
      app.run(debug=True, port=8080)
::


Flask Routes
------------
The Flask server has the following routes and functions:

Sites
~~~~~
The following routes are used to display the different sites of the application.

.. autofunction:: main.index

.. autofunction:: main.dashboard

.. autofunction:: main.matches

.. autofunction:: main.standings

Setup-/ Login-Functions
~~~~~~~~~~~~~~~~~~~~~~~
The following routes are used to setup a tournament or login and logout of the application.

.. autofunction:: main.process_form

.. autofunction:: main.login_manager

.. autofunction:: main.login_referee

.. autofunction:: main.login_fencer

Get Tournament Infos
~~~~~~~~~~~~~~~~~~~~
The following routes are used to get tournament infos from the server. They are used to display the tournament infos on different Sites, but first and foremost the dashboard.

.. autofunction:: main.get_dashboard_infos

.. autofunction:: main.get_matches

.. autofunction:: main.get_standings

.. autofunction:: main.matches_left

Pushing Data to the Server
~~~~~~~~~~~~~~~~~~~~~~~~~~
The following routes are used to push data to the server. They are used to update the tournament infos on the server, like pushing Scores, setting matches active or advancing in stages.

.. autofunction:: main.push_score

.. autofunction:: main.set_active

.. autofunction:: main.next_stage

Testing-Tools
~~~~~~~~~~~~~
The following routes are used only for testing purposes. They are used to test the functionality of the application.

.. autofunction:: main.simulate_current


