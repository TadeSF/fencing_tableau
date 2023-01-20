function get_standings() {
    let group_query = document.getElementById('Group_Number').innerHTML
    fetch('update/' + group_query)
    .then(response => response.json())
    .then(response => {
        let standings = response["standings"]
        let stage = response["stage"]
        let max_elimination_ranks = response["first_elimination_round"]
        update_standings(standings, stage, max_elimination_ranks)
    })
}

function get_flag(country) {
  return new Promise((resolve, reject) => {
    // Check if the file is already in cache
    if (flagCache[country]) {
      resolve(flagCache[country]);
      return;
    }

    fetch('/static/flags/' + country.toLowerCase() + '.svg')
      .then(response => response.text())
      .then(response => {
        // Add the flag to the cache
        flagCache[country] = response;
        resolve(response);
      })
      .catch(error => {
        reject(error);
      });
  });
}

const flagCache = {};

function clearTable(table) {
    // Get the first row (the row that contains the headers)
    var firstRow = table.rows[0];

    // Clear the table, starting from the second row (the first row is the row that contains the headers)
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }
}


async function update_standings(rankings, stage, max_elimination_ranks) {
    let standings = document.getElementById('standings_table')

    // Remove all rows from the table
    clearTable(standings);

    // Add the new, updated rows
    for (const element of rankings) {
        let row = document.createElement('tr')
        let id = document.createElement('td')
        id.style.display = "none"
        let rank = document.createElement('td')
        let nationality = document.createElement('td')
        let name = document.createElement('td')
        let club = document.createElement('td')
        let win_percentage = document.createElement('td')
        let win_lose = document.createElement('td')
        let point_difference = document.createElement('td')
        let points_for = document.createElement('td')
        let points_against = document.createElement('td')

        let id_text = document.createTextNode(element["id"])
        let rank_text = document.createTextNode(element["rank"])
        let name_text = document.createTextNode(element["name"])
        let club_text = document.createTextNode(element["club"])

        if (element["nationality"].length == 3) {
            let flag = document.createElement('div')
            flag.className = "flag"
            // Load the SVG string from the server
            let svgString = await get_flag(element["nationality"]);

            // Parse the SVG string into a DocumentFragment
            let parser = new DOMParser();
            let doc = parser.parseFromString(svgString, 'image/svg+xml');
            let svg = doc.querySelector('svg');

            // Append the DocumentFragment to the flag element
            flag.appendChild(svg);

            // Set the width of the SVG
            svg.style.width = '30px';
            nationality.appendChild(flag)
        } else {
            let nationality_text = document.createTextNode(element["nationality"])
            nationality.appendChild(nationality_text)
        }

        let win_percentage_text = document.createTextNode(element["win_percentage"])
        if (element["win_lose"] == undefined) {element["win_lose"] = "0-0"}
        let win_lose_text = document.createTextNode(element["win_lose"])
        if (element["points_difference"] == undefined || element["points_difference"] == "0") {element["points_difference"] = "±0"}
        let point_difference_text = document.createTextNode(element["points_difference"])
        let points_for_text = document.createTextNode(element["points_for"])
        let points_against_text = document.createTextNode(element["points_against"])

        id.appendChild(id_text)
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

        row.appendChild(id)
        row.appendChild(rank)
        row.appendChild(nationality)
        row.appendChild(name)
        row.appendChild(club)
        row.appendChild(win_percentage)
        row.appendChild(win_lose)
        row.appendChild(point_difference)
        row.appendChild(points_for)
        row.appendChild(points_against)

        if (stage !== "Preliminary Round") {
            if (element["eliminated"] === true && stage !== "Finished") {
                row.classList.add("eliminated")
            } else if (element["eliminated"] === true && stage === "Finished") {
                row.classList.add("normal")
            } else {
                row.classList.add("not-eliminated")
            }
            if (element["rank"] <= 3) {
                row.classList.add("podium")
            }
        } else {
            if (element["rank"] <= max_elimination_ranks) {
                row.classList.add("advancing")
            } else if (max_elimination_ranks == null) {
                row.classList.add("normal")
            } else {
                row.classList.add("eliminated")
            }
        }

        row.onclick = function() {
            open_fencer_window(element["id"])
        }

        standings.appendChild(row)
    }
}

window.onload = function() {
    get_standings()
  };

// loop to update the standings every 90 seconds
setInterval(get_standings, 60000)

// Listen for messages from the parent window
window.addEventListener('message', function(event) {
  // Check if the message is 'callFunction'
  if (event.data === 'update') {
    // Call the function
    get_standings();
  }
});

window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};

function open_fencer_window(id) {
    let url = "fencer/" + id
    window.open(url, "_blank")
}