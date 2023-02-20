Userguide
=========
This is a userguide for the Web-Application. It is not a tutorial, but it will help you to understand the program and how to use it to its full potential.

The Tournament Master
---------------------
The Tournament Master is the creator and manager of the tournament. He has the highest clearence and can do (almost) anything. It is advised that he uses a desktop computer or laptop to use the program. The functionality includes the possibilities to display information in a seperate Window (e.g. for a beamer or big screen).

The Tournament Master can:
    - Create a new tournament
    - Manage all stages of the tournament
    - Assign Pistes to matches
    - Ban a fencer from the tournament
    - Change the status of a match
    - Input Scores
    - Manage all settings
    - Change Fencer Information


Creating a new tournament
*************************
When creating a new tournament, the Tournament Master has to fill in/provide the following information/files:

- Tournament Name
    The name of the tournament. This name will be publicly displayed in the list of all tournaments.
- Tournament Location (optional)
    The location of the tournament. This information will not be public but can be accessed with the right tournament ID.
- Startlist (in .csv format)
    The Startlist must have a certain format. We provide a template_, a sample-file_ and even a dedicated Startlist-Builder_. The Startlist-Builder is a program that helps you to create a startlist. It is not mandatory to use it, but it is highly recommended.
    Please refer to the coresponding section `The Startlist`_ below for more information.
- Number of available pistes
    Must be a fixed number and cannot be changed after the tournament is created.
- Number of preliminary rounds
    Select the number of preliminary rounds that will be played. In each preliminary round, the groups are reassigned according to the standings (or in the first round the Startlist). The number of preliminary rounds cannot be changed after the tournament is created. Defaults to 1. If you want to skip the preliminary rounds and start directly with the elimination round, set the field to None.
- Number of preliminary groups
    Select the number of preliminary groups. The number of preliminary groups cannot be changed after the tournament is created. Defaults to "Auto", which means that the number of groups is calculated automatically according to FIE Guidlines and the total number of fencers.
- First elimination round
    Select the first elimination round. The number of elimination rounds cannot be changed after the tournament is created. Defaults to "Auto", which means that the first elimination round is the next bigger power of 2 after the number of fencers (to make elimination work, wildcards are assigned to the first fencers in the first elimination round). If you want to cap the number of elimination rounds (e.g. you want only the top 32 fencers to advance), set the field to the desired number.
- Elimination mode
    This Web-Application offers three different tournament modes.

    - Direct Elimination ("KO") (default)
    - Repechage (not yet implemented)
    - Direct Elimination with Placement Matches
- Master Password
    The Master Password is used to protect the tournament from unauthorized access. When creating a tournament or logging in as master, a cookie is set in the browser of the user and his/her status is saved.

.. _template: https://fencewithfriends.online/csv-template
.. _sample-file: https://fencewithfriends.online/csv-sample
.. _Startlist-Builder: https://fencewithfriends.online/build-your-startlist

The Startlist
*************
The Startlist is a comma delimited CSV (.csv) file that contains all information about the fencers. It is mandatory to provide a Startlist when creating a tournament. The Startlist must have a certain format. We provide a template_, a sample-file_ and even a dedicated Startlist-Builder_. The Startlist-Builder is a program that helps you to create a startlist. It is not mandatory to use it, but it is highly recommended.

The first line contains the column headers. The following columns (with one header line) are required:
        
- ``Name``
    The name of the fencer
    (mandatory)

- ``Club``
    The club of the fencer – to avoid display annomalies, please just use an acronym (e.g. NOT "Turngemeinde in Berlin 1848 e.V.", but "TIB")
    (mandatory)

- ``Nationality``
    The Nationality of the fencer. Must be a three-letter alpha-3 country code (e.g. "GER" for Germany, "FRA" for France, "USA" for the United States of America, etc.). For a list of all country codes, please refer to https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3.
    
    .. attention:: If you get an Error trying to upload your startlist with the message ``Invalid Country Code``, please check your startlist for any country codes that are not three letters long. If you are sure that all country codes are correct, you can use ``XXX`` as a placeholder (this will display the flag of the United Nations) and report the missing country code to us.

    (mandatory)

- ``Gender``
    The gender of the fencer. Must be either
        
    - "M"
    - "F"
    - "D" for divers

    (optional, but must be in header)

- ``Handedness`` 
    The handedness of the fencer. Must be either

    - "R"
    - "L" 

    (optional, but must be in header)

- ``Age``
    The age of the fencer. Must be a positiv integer, either

    - (preferably) the age (e.g. 23)
    - the birthyear (e.g. 1999, age calculations might be one year off due to missing birthday information)
    - the birthday (format: YYYY-MM-DD, e.g. 1999-01-01)

    (optional, but must be in header)

.. attention:: There is no specific ``Start Number`` column. The start number is automatically assigned to the fencers according to the Startlist. If you want to have a sorted Startlist Fencer #1 is the best (e.g. highest elo), you just have to sort the Startlist accordingly with the first row after the header being Fencer #1.

Using the Dashboard
*******************
The Dashboard is the main page of the Web-Application for the master. It is the first page that is displayed when you log in as Tournament Master. It contains all information about the current state of the tournament. The Dashboard is divided into three sections:

Tournament Information
++++++++++++++++++++++
The Tournament Information section contains all information about the current tournament. It includes the following information:

- Tournament Name
- Tournament Location
- Tournament ID
- The current status of the tournament (e.g. "Preliminary Round 1", "Elimination Round 1", "Finished")
- Detailed Information about the tournament itself (e.g. number of fencers, number of groups, number of elimination rounds, etc.)

Dashboard Buttons
#################
The Dashboard contains several buttons that can be used to control the tournament. The following buttons are (depending on the state) available:

- ``Advance to next stage``
    This button advances the tournament to the next stage (e.g. from Preliminary Round 1 to Preliminary Round 2 or Elimination Round of 16 to Round of 8).

- ``QR-Code``
    This button opens a new window with a genereted QR-Code and Link that leads to the fencer-login page. This QR-Code can be used to display the fencer-login page on a screen in the tournament hall.

- ``Tableau``
    This button opens a new window with a Tableau that displays the tableaus of the current preliminary round. Not available during elimination rounds.

- ``Simulation``
    This button is only available if specified in the tournament configurations at creation. It simulates all matches of the current stage. This feature only exists for testing purposes.


Matches
+++++++
The Matches section contains all information about the matches of the current stage. It includes the following information:

- The group/stage of the match
- The piste of the match (dynamic, assigned automatically, can be changed by the master)
- The fencers of the match
- The score (if the match is finished)

Matches Buttons
###############
Each match contains several buttons that can be used to control the match. The following buttons are (depending on the state) available:

- ``Piste``
    This Button opens a option menu that allows the master to change settings of the assigned piste.
    
    .. attention:: The piste assignment is dynamic and should work automatically and without any user interaction. But since the real world is not perfect and it is sometimes necessary to change the piste assignment, this option menu is available for the master.

    The following settings are – depending on the assingment state of a match - available:

        - ``Assign Piste Input`` and ``Send``
            Input and button allow the master to assign the match to a piste. The master has to input the piste number in the ``Assign Piste Input``. The piste will be assigned to the match.
        
            .. attention:: If the piste is already assigned to another match, the other match will be unassigned from the piste.
        
        - ``Unassign Piste``
            This button unassigns the match from the piste. The piste will be available for other matches.

        - ``High Priority``
            This button sets the priority of the match to high. This means that the match will be assigned the next free piste that is available, even if other matches are listed before this match. This is useful if a match is running late and the master wants to assign the next match to a piste as soon as possible.

        - ``Low Priority``
            This button sets the priority of the match to low. This means that this match will not be assigned to a piste if there are other matches of higher or normal priority. This is useful if a fencer is temporarily not available (e.g. needs medical attention or just a break) and the master wants to assign the next match to a piste as soon as possible without doing it manually.

    .. tip:: The Piste Button is animated to indicate the state of the match. This includes blinking when the match is assigned to a piste but the piste is still occupied, flashing orange when the match is assigned to a piste and the piste is free, or pulsing green when the match is ongoing on the piste.
        
    .. warning:: The piste Button may not be available if the match is already ongoing or finished.

- ``Results``
    This Button opens a option menu that allows the master to input or change the results of the match OR to start the match if it is not already started.
    The score is set by inputting the score of each fencer in the corresponding input field and confirming by pressing the ``Send`` button. The score will be updated and the match will be marked as finished.

    .. attention:: If the match is already finished, the score will be overwritten by the new score.

    .. tip:: The Results Button is animated to indicate the state of the match. This includes pulsing the logo when the match is ready to be started or "loading" green when the match is ongoing.

    .. warning:: The Results Button may not be available if the match is not ready to be started (e.g. if no piste is yet assigned to the match).

    .. danger:: The "Start Match" option is already available if another match is still ongoing on the same piste. THIS IS AN EXPERIMENTAL FEATURE! It is not guaranteed that the match will be started correctly. If you want to start a match on a piste that is already occupied, you have to make sure that the match on the piste is finished before starting the new match. If you are not sure, do not use this feature. It may have unexpected implications on the tournament and the management process.

- ``Match Options``
    This Button opens a option menu that allows the master to change settings of the match. As of yet, there are no settings available. The dummy buttons that are displayed have no functionality.


The Referee
-----------
Hello World

The Fencer
----------
Hello World