function get_standings() {
    let group_query = document.getElementById("group_filter").value
    let gender_query = document.getElementById("gender_filter").value
    let handedness_query = document.getElementById("handedness_filter").value
    let age_query= document.getElementById("age_filter").value
    
    if (group_query === "all" || group_query === "") {
        group_query = ""
    } else {
        group_query = "group=" + group_query
    }

    if (gender_query != "") {
        gender_query = "gender=" + gender_query
    }

    if (handedness_query != "") {
        handedness_query = "handedness=" + handedness_query
    }

    if (age_query != "") {
        age_query = "age=" + age_query
    }

    full_query = ""
    if (group_query != "" || gender_query != "" || handedness_query != "" || age_query != "") {
        full_query = "?"
    }

    if (group_query != "") {
        full_query += group_query
    }

    if (gender_query != "") {
        if (full_query != "?") {
            full_query += "&"
        }
        full_query += gender_query
    }

    if (handedness_query != "") {
        if (full_query != "?") {
            full_query += "&"
        }
        full_query += handedness_query
    }

    if (age_query != "") {
        if (full_query != "?") {
            full_query += "&"
        }
        full_query += age_query
    }


    fetch('standings/update' + full_query)
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

function clearTable() {
    document.getElementById('tablebody').innerHTML = "";
}


async function update_standings(rankings, stage, max_elimination_ranks) {
    let standings = document.getElementById('standings_table')
    console.log(standings)

    // Remove all rows from the table
    clearTable(standings);

    // Add the new, updated rows
    for (const element of rankings) {
        let item = document.createElement('div')
        item.classList.add("item")
        item.dataset.fencer_id = element["id"]

        let rank = document.createElement('div')
        rank.classList.add("cell", "first-column", "rank")
        if (element["rank"] == 1) {
            rank.innerHTML = '<i class="fa-solid fa-medal"></i>'
            rank.style.fontSize = "0.85em"
        } else {
            rank.innerHTML = element["rank"]
        }
        
        let flag = document.createElement('div')
        flag.classList.add("cell", "flag")
        let svgString = await get_flag(element["nationality"]);
        let parser = new DOMParser();
        let doc = parser.parseFromString(svgString, 'image/svg+xml');
        let svg = doc.querySelector('svg');
        flag.appendChild(svg);
        
        let name = document.createElement('div')
        name.classList.add("cell", "name")
        name.innerHTML = element["name"]
        
        let club = document.createElement('div')
        club.classList.add("cell", "club")
        club.innerHTML = element["club"]

        let win_percentage = document.createElement('div')
        win_percentage.classList.add("cell", "win-percentage")
        win_percentage.innerHTML = element["win_percentage"]

        let win_lose = document.createElement('div')
        win_lose.classList.add("cell", "win-lose")
        if (element["win_lose"] == undefined) {element["win_lose"] = "0-0"}
        win_lose.innerHTML = element["win_lose"]

        let point_difference = document.createElement('div')
        point_difference.classList.add("cell", "point-difference", "last-column-very-small")
        if (element["points_difference"] == undefined || element["points_difference"] == "0") {element["points_difference"] = "±0"}
        point_difference.innerHTML = element["points_difference"]

        let points_for = document.createElement('div')
        points_for.classList.add("cell", "points-for")
        points_for.innerHTML = element["points_for"]

        let points_against = document.createElement('div')
        points_against.classList.add("cell", "points-against", "last-column-small")
        points_against.innerHTML = element["points_against"]

        let gender = document.createElement('div')
        gender.classList.add("cell", "gender")
        if (element["gender"] == "M") {
            gender.innerHTML = '<i class="fa-solid fa-mars"></i>'
        } else if (element["gender"] == "F") {
            gender.innerHTML = '<i class="fa-solid fa-venus"></i>'
        } else if (element["gender"] == "D") {
            gender.innerHTML = '<i class="fa-solid fa-genderless"></i>'
        } else {
            gender.innerHTML == ''
        }

            
            let handedness = document.createElement('div')
        handedness.classList.add("cell", "handedness")
        handedness.innerHTML = element["handedness"]

        let age = document.createElement('div')
        age.classList.add("cell", "age", "last-column")
        age.innerHTML = element["age"]

        item.appendChild(rank)
        item.appendChild(flag)
        item.appendChild(name)
        item.appendChild(club)
        item.appendChild(win_percentage)
        item.appendChild(win_lose)
        item.appendChild(point_difference)
        item.appendChild(points_for)
        item.appendChild(points_against)
        item.appendChild(gender)
        item.appendChild(handedness)
        item.appendChild(age)

        if (stage !== "Preliminary Round") {
            if (element["eliminated"] === true && stage !== "Finished") {
                item.classList.add("eliminated")
            } else if (element["eliminated"] === true && stage === "Finished") {
                item.classList.add("normal")
            } else {
                item.classList.add("not-eliminated")
            }
            if (element["rank"] <= 3) {
                item.classList.add("podium")
            }
        } else {
            if (element["rank"] <= max_elimination_ranks) {
                item.classList.add("advancing")
            } else if (max_elimination_ranks == null) {
                item.classList.add("normal")
            } else {
                item.classList.add("eliminated")
            }
        }

        item.onclick = function() {
            open_fencer_window(element["id"])
        }

        document.getElementById("tablebody").appendChild(item)
    }
}

function updateFilter() {
    let num_groups = document.getElementById("group_filter").dataset.num_groups
    let group_filter = document.getElementById("group_filter")
    group_filter.innerHTML = ""
    let all_option = document.createElement("option")
    all_option.value = ""
    all_option.text = "All Groups"
    group_filter.appendChild(all_option)
    for (let i = 1; i <= num_groups; i++) {
        let option = document.createElement("option")
        option.value = i
        option.text = "Group " + i
        group_filter.appendChild(option)
    }
    if (group_filter.dataset.requested_group === "all") {
        group_filter.value = ""
    } else {
        group_filter.value = group_filter.dataset.requested_group
    }
}

function open_in_new_tab() {
    window.open("standings", "_blank")
}

window.onload = function() {
    updateFilter()
    // if not an iframe, update the matches
    if (window.self === window.top) {
        document.getElementById("open_in_new_tab").style.display = "none"
        get_standings()
    }

}

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

function savePDF() {
    header = document.getElementById("header")
    header.position = "static"
    tableheaders = document.getElementsByTagName("th")
    for (let i = 0; i < tableheaders.length; i++) {
        tableheaders[i].style.position = "static"
    }
    window.print()
    header.position = "sticky"
    for (let i = 0; i < tableheaders.length; i++) {
        tableheaders[i].style.position = "sticky"
    }
}

window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};

function open_fencer_window(id) {
    let url = "fencer/" + id
    window.open(url, "_blank")
}