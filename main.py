import time
import eel


eel.init('web')
# eel.start('main.html', block=False)

eel.start('standings.html', block=False, size=(500, 1000), port=8001, mode='chrome')
eel.start('matches.html', block=False, size=(1000, 500), port=8002)


# Sample data

standings = [
    {
        "rank": 1,
        "name": "Tade Strehk",
        "club": "TIB",
        "nationality": "DEU",
        "flag": open('web/flags/deu.svg', 'r').read(),
        "win_percentage": 0.75,
        "win_lose": "5 - 1",
        "point_difference": "+4",
        "points_for": 15,
        "points_against": 11,
    },
    {
        "rank": 2,
        "name": "Olga Iwnanowska",
        "club": "UP",
        "nationality": "POL",
        "flag": open('web/flags/pol.svg', 'r').read(),
        "win_percentage": 0.5,
        "win_lose": "5-3",
        "point_difference": "-2",
        "points_for": 20,
        "points_against": 22,
    },
]
stage = "Final"
    

eel.update_standings(standings, stage)()
time.sleep(10)