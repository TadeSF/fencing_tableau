function update_standings(rankings, stage) {
    var standings = document.getElementById('standings_table')

    // Change stage headline
    var stage_item = document.getElementById('stage')
    stage_item.innerHTML = stage

    // Remove all rows from the table
    //$("#standings_table tr").remove();

    // Add the new, updated rows
    for (var i = 0; i < rankings.length; i++) {
        var row = document.createElement('tr')
        var rank = document.createElement('td')
        var nationality = document.createElement('td')
        var name = document.createElement('td')
        var club = document.createElement('td')
        var win_percentage = document.createElement('td')
        var win_lose = document.createElement('td')
        var point_difference = document.createElement('td')
        var points_for = document.createElement('td')
        var points_against = document.createElement('td')

        var rank_text = document.createTextNode(rankings[i]["rank"])
        var name_text = document.createTextNode(rankings[i]["name"])
        var club_text = document.createTextNode(rankings[i]["club"])

        if (rankings[i]["flag"] != null) {
            var flag = document.createElement('div')
            flag.className = "flag"
            flag.innerHTML = rankings[i]["flag"]
            flag.querySelector("svg").style.width = "30px"
            nationality.appendChild(flag)
        } else {
            var nationality_text = document.createTextNode(rankings[i]["nationality"])
            nationality.appendChild(nationality_text)
        }

        var win_percentage_text = document.createTextNode((rankings[i]["win_percentage"] * 100))
        var win_lose_text = document.createTextNode(rankings[i]["win_lose"])
        var point_difference_text = document.createTextNode(rankings[i]["point_difference"])
        var points_for_text = document.createTextNode(rankings[i]["points_for"])
        var points_against_text = document.createTextNode(rankings[i]["points_against"])


        rank.appendChild(rank_text)
        name.appendChild(name_text)
        club.appendChild(club_text)
        win_percentage.appendChild(win_percentage_text)
        win_lose.appendChild(win_lose_text)
        point_difference.appendChild(point_difference_text)
        points_for.appendChild(points_for_text)
        points_against.appendChild(points_against_text)

        nationality.className = "cell-nationality"
        name.className = "cell-name"
        rank.className = "cell-rank"

        row.appendChild(rank)
        row.appendChild(nationality)
        row.appendChild(name)
        row.appendChild(club)
        row.appendChild(win_percentage)
        row.appendChild(win_lose)
        row.appendChild(point_difference)
        row.appendChild(points_for)
        row.appendChild(points_against)

        standings.appendChild(row)
    }
}

eel.expose(update_standings)