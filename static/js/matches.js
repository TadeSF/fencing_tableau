const tournament_id = document.body.dataset.tournament_id

if (window.self === window.top) {
    document.body.classList.add('not-in-iframe');
} else {
    document.body.classList.add('in-iframe');
}


function get_matches() {
    fetch('matches/update')
    .then(response => response.json())
    .then(response => {
        console.log(response)
        let matches = response["matches"]
        update_matches(matches)
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
    let tablebody = document.getElementById('tablebody')
    tablebody.innerHTML = ""
}

function parseSVG(svgString) {
    // Parse the SVG string into a DocumentFragment
    let parser = new DOMParser();
    let doc = parser.parseFromString(svgString, 'image/svg+xml');
    let svg = doc.querySelector('svg');
    return svg;
}

async function update_matches(matches) {
    // render placeholders for all matches
    const matches_table = document.getElementById("tablebody")
    let num_matches = function() {
        let num_matches = 0
        for (const element of matches_table.children) {
            if (element.style.display != "none") {
                num_matches++
            }
        }
        return num_matches
    }()

    matches_table.innerHTML = ""
    for (let i = 0; i < num_matches; i++) {
        let placeholder = document.createElement('div')
        placeholder.classList.add("cell", "placeholder")
        matches_table.appendChild(placeholder)
    }

    let matches_array = []
    
    // wait for 1 second
    await new Promise(r => setTimeout(r, 1000));

    // Add the new, updated rows
    for (const element of matches) {
        let item = document.createElement('div')
        item.className = "item"
        item.id = "match-" + element["id"]
        item.dataset.match_id = element["id"]
        item.dataset.completed = element["complete"]
        item.dataset.ongoing = element["ongoing"]
        item.dataset.priority = element["priority"]

        let group = document.createElement('div')
        group.classList.add("group", "cell", "first-column")
        if (element["group"] != null) {
            group.innerHTML = element["group"]
        } else {
            group.innerHTML = "F"
        }

        let piste = document.createElement('div')
        let piste_wrapper = document.createElement('div')
        piste_wrapper.innerHTML = element["piste"]
        piste_wrapper.classList.add("piste-wrapper")
        piste.classList.add("piste", "cell")
        if (element["complete"] === true) {
            piste_wrapper.classList.add("piste-completed")
        } else if (element["ongoing"] === true) {
            piste_wrapper.classList.add("piste-ongoing")
        } else if (element["piste_occupied"] === false) {
            piste_wrapper.classList.add("piste-empty")
            piste.onclick = function() {
                openPisteOptions(item, matches_table, element["id"])
            }
        } else if (element["piste"] != "TBA") {
            piste_wrapper.classList.add("piste-staged")
            piste.onclick = function() {
                openPisteOptions(item, matches_table, element["id"])
            }
        } else {
            piste_wrapper.classList.add("piste-tba")
            if (element["priority"] == 1) {
                piste_wrapper.innerHTML = '<i class="fa-solid fa-circle-arrow-up"></i>'
            } else if (element["priority"] == -1) {
                piste_wrapper.innerHTML = '<i class="fa-solid fa-circle-arrow-down"></i>'
            }
            piste.onclick = function() {
                openPisteOptions(item, matches_table, element["id"])
            }
        }
        piste.appendChild(piste_wrapper)

        let score = document.createElement('div')
        score.classList.add("score", "cell")
        if (element["green_score"] != 0 || element["red_score"] != 0) {
            score.innerHTML = element["red_score"] + " : " + element["green_score"]
        } else {
            score.innerHTML = " : "
        }

        let red = document.createElement('div')
        red.dataset.fencer_id = element["red_id"]
        red.classList.add("red", "cell")
        let red_wrapper = document.createElement('div')
        red_wrapper.classList.add("Name-Banner")
        let red_name = document.createElement('div')
        red_name.classList.add("name")
        let red_flag = document.createElement('div')
        red_flag.classList.add("flag")
        let red_svgString = await get_flag(element["red_nationality"]);
        let red_svg = parseSVG(red_svgString);
        red_flag.appendChild(red_svg);
        red_name.innerHTML = element["red"]
        red_wrapper.appendChild(red_flag)
        red_wrapper.appendChild(red_name)
        if (element["red"].includes("Wildcard") == false) {
            red.onclick = function() {
                window.open("/" + tournament_id + "/fencer/" + element["red_id"], "_blank")
            }
        } else {
            red.classList.add("wildcard")
        }
        red.appendChild(red_wrapper)

        let green = document.createElement('div')
        green.dataset.fencer_id = element["green_id"]
        green.classList.add("green", "cell")
        let green_wrapper = document.createElement('div')
        green_wrapper.classList.add("Name-Banner")
        let green_name = document.createElement('div')
        green_name.classList.add("name")
        let green_flag = document.createElement('div')
        green_flag.classList.add("flag")
        let green_svgString = await get_flag(element["green_nationality"]);
        let green_svg = parseSVG(green_svgString);
        green_flag.appendChild(green_svg);
        green_name.innerHTML = element["green"]
        green_wrapper.appendChild(green_flag)
        green_wrapper.appendChild(green_name)
        if (element["green"].includes("Wildcard") == false) {
            green.onclick = function() {
                window.open("/" + tournament_id + "/fencer/" + element["green_id"], "_blank")
            }
        } else {
            green.classList.add("wildcard")
        }
        green.appendChild(green_wrapper)

        let forward_button = document.createElement('div')
        forward_button.classList.add("forward", "cell")
        let forward_button_wrapper = document.createElement('div')
        forward_button_wrapper.classList.add("option-button-wrapper")
        let forward_icon = document.createElement('i')
        if (element["complete"] == true) {
            forward_button_wrapper.classList.add("forward-button-completed")
            forward_icon.classList.add("fa-solid", "fa-check")
            forward_button.onclick = function() {
                openScoreOptions(item, matches_table, element["id"])
            }
            forward_button.onmouseenter = function() {
                forward_icon.classList.remove("fa-check")
                forward_icon.classList.add("fa-edit")
            }
            forward_button.onmouseleave = function() {
                forward_icon.classList.remove("fa-edit")
                forward_icon.classList.add("fa-check")
            }
        } else if (element["ongoing"] == true) {
            forward_button_wrapper.classList.add("forward-button-ongoing")
            forward_icon.classList.add("fa-solid", "fa-spinner", "fa-spin")
            forward_button.onclick = function() {
                openScoreOptions(item, matches_table, element["id"])
            }
            forward_button.onmouseenter = function() {
                forward_icon.classList.remove("fa-spin", "fa-spinner")
                forward_icon.classList.add("fa-trophy")
            }
            forward_button.onmouseleave = function() {
                forward_icon.classList.remove("fa-trophy")
                forward_icon.classList.add("fa-spin", "fa-spinner")
            } 
        } else if (element["piste"] != "TBA") {
            forward_button_wrapper.classList.add("forward-button-staged")
            forward_button.onclick = function() {
                match_set_active(element["id"])
            }
            forward_icon.classList.add("fa-solid", "fa-play")
            if (element["piste_occupied"] == false) {
                forward_icon.classList.add("fa-beat")
            }
        } else {
            forward_button_wrapper.classList.add("forward-button-blocked")
            forward_icon.classList.add("fa-solid", "fa-ban")
        }
        forward_button_wrapper.appendChild(forward_icon)
        forward_button.appendChild(forward_button_wrapper)

        let options_button = document.createElement('div')
        options_button.classList.add("options", "cell", "last-column")
        let options_button_wrapper = document.createElement('div')
        options_button_wrapper.classList.add("option-button-wrapper")
        let options_icon = document.createElement('i')
        options_icon.classList.add("fa-solid", "fa-gear")
        options_button_wrapper.appendChild(options_icon)
        options_button.onclick = function() {
            openMatchOptions(item, matches_table, element["id"])
        }
        options_button.appendChild(options_button_wrapper)

        item.appendChild(group)
        item.appendChild(piste)
        item.appendChild(red)
        item.appendChild(score)
        item.appendChild(green)
        item.appendChild(forward_button)
        item.appendChild(options_button)

        
        matches_array.push(item)
        
    }
    
    clearTable();

    for (const element of matches_array) {
        matches_table.appendChild(element)
    }

    toggleFilter(true)
}

// Set the time for the fade-in and fade-out animations
const panelAnimationTime = 300

function hideAllOptionPanels(callback) {
    const match_options = document.getElementById("match_options")
    const piste_options = document.getElementById("piste_options")
    const score_options = document.getElementById("score_options")

    let count = 0

    if (match_options != null) {
        match_options.style.animation = "fade-out " + panelAnimationTime + "ms ease-in-out"
        setTimeout(function() {
            match_options.remove()
            count++
            if (count === 3) {
                callback()
            }
        }, panelAnimationTime + 10)
    } else {
        count++
    }

    if (piste_options != null) {
        piste_options.style.animation = "fade-out " + panelAnimationTime + "ms ease-in-out"
        setTimeout(function() {
            piste_options.remove()
            count++
            if (count === 3) {
                callback()
            }
        }, panelAnimationTime + 10)
    } else {
        count++
    }

    if (score_options != null) {
        score_options.style.animation = "fade-out " + panelAnimationTime + "ms ease-in-out"
        setTimeout(function() {
            score_options.remove()
            count++
            if (count === 3) {
                callback()
            }
        }, panelAnimationTime + 10)
    } else {
        count++
    }

    if (count === 3) {
        callback()
    }
}

function openPisteOptions(siblingElement, parentElement, match_id) {
    // if the piste options are already open in the same match, set a boolean flag to true
    let options_open = false
    if (document.getElementById("piste_options") != null) {
        // if the element comes after the sibling in the DOM, set the flag to true
        if (document.getElementById("piste_options") == siblingElement.nextSibling) {
            options_open = true
        }   
    }


    hideAllOptionPanels(function() {

        if (options_open === true) {
            return;
        }

        let piste_options = document.createElement('div')
        piste_options.id = "piste_options"

        let assign_piste_input = document.createElement('input')
        assign_piste_input.type = "text"
        assign_piste_input.placeholder = "Assign Piste"
        assign_piste_input.id = "assign_piste_input"
        assign_piste_input.onkeyup = function(event) {
            // check if it is a number
            if (isNaN(this.value)) {
                this.value = ""
            } else if (parseInt(this.value) > document.body.dataset.pistes) {
                this.value = ""
            }

            if (event.code == 13) {
                assign_piste(match_id, assign_piste_input.value)
            }
        }

        let assign_piste_button = document.createElement('div')
        assign_piste_button.innerHTML = '<i class="fas fa-check"></i>'
        assign_piste_button.onclick = function() {
            if (assign_piste_input.value != "") {
                assign_piste(match_id, assign_piste_input.value)
            }
        }

        let unassign_piste_button = document.createElement('div')
        unassign_piste_button.innerHTML = '<i class="fas fa-trash-can"></i>'
        unassign_piste_button.onclick = function() {
            remove_piste_assignment(match_id)
        }

        let high_priority_piste_button = document.createElement('div')
        high_priority_piste_button.innerHTML = '<i class="fa-solid fa-circle-arrow-up"></i>'
        high_priority_piste_button.onclick = function() {
            if (siblingElement.dataset.priority == 1) {
                prioritize_match(match_id, 0)
                document.body.dataset.priority = 0
                high_priority_piste_button.classList.remove("priority-active")
            } else {
                prioritize_match(match_id, 1)
                document.body.dataset.priority = 1
                high_priority_piste_button.classList.add("priority-active")
            }
        }

        let low_priority_piste_button = document.createElement('div')
        low_priority_piste_button.innerHTML = '<i class="fa-solid fa-circle-arrow-down"></i>'
        low_priority_piste_button.onclick = function() {
            if (siblingElement.dataset.priority == -1) {
                prioritize_match(match_id, 0)
                document.body.dataset.priority = 0
                low_priority_piste_button.classList.remove("priority-low-active")
            } else {
                prioritize_match(match_id, -1)
                document.body.dataset.priority = -1
                low_priority_piste_button.classList.add("priority-low-active")
            }
        }

        if (siblingElement.dataset.priority == 1) {
            high_priority_piste_button.classList.add("priority-active")
        } else if (siblingElement.dataset.priority == -1) {
            low_priority_piste_button.classList.add("priority-low-active")
        }

        piste_options.appendChild(assign_piste_input)
        piste_options.appendChild(assign_piste_button)

        piste_number = siblingElement.children[1].children[0].innerHTML
        if (piste_number == "TBA" || piste_number == "<i class=\"fa-solid fa-circle-arrow-down\"></i>" || piste_number == "<i class=\"fa-solid fa-circle-arrow-up\"></i>") {
            piste_options.appendChild(high_priority_piste_button)
            piste_options.appendChild(low_priority_piste_button)
        } else {
            piste_options.appendChild(unassign_piste_button)
        }

        piste_options.style.animation = "fade-in " + panelAnimationTime + "ms ease-in-out"

        parentElement.insertBefore(piste_options, siblingElement.nextSibling)
    });
}

function openMatchOptions(siblingElement, parentElement, match_id) {
    // if the piste options are already open in the same match, set a boolean flag to true
    let options_open = false
    if (document.getElementById("match_options") != null) {

        // if the element comes after the sibling in the DOM, set the flag to true
        if (document.getElementById("match_options") == siblingElement.nextSibling) {
            options_open = true
        }   
    }


    hideAllOptionPanels(function() {

        if (options_open === true) {
            return;
        }

        let match_options = document.createElement('div')
        match_options.id = "match_options"
        
        let button1 = document.createElement('div')
        button1.innerHTML = '<i class="fa-solid fa-question"></i>'

        let button2 = document.createElement('div')
        button2.innerHTML = '<i class="fa-solid fa-question"></i>'

        let button3 = document.createElement('div')
        button3.innerHTML = '<i class="fa-solid fa-question"></i>'

        match_options.appendChild(button1)  
        match_options.appendChild(button2)
        match_options.appendChild(button3)
        
        match_options.style.animation = "fade-in " + panelAnimationTime + "ms ease-in-out"

        parentElement.insertBefore(match_options, siblingElement.nextSibling)
    });
}

function openScoreOptions(siblingElement, parentElement, match_id) {
    // if the piste options are already open in the same match, set a boolean flag to true
    let options_open = false
    if (document.getElementById("score_options") != null) {

        // if the element comes after the sibling in the DOM, set the flag to true
        if (document.getElementById("score_options") == siblingElement.nextSibling) {
            options_open = true
        }   
    }

    hideAllOptionPanels(function() {

        if (options_open === true) {
            return;
        }

        let score_options = document.createElement('div')
        score_options.id = "score_options"

        let red_score_input = document.createElement('input')
        red_score_input.type = "text"
        red_score_input.placeholder = "Red Score"
        red_score_input.id = "red_score_input"
        red_score_input.onkeyup = function(event) {
            // check if it is a number
            if (isNaN(this.value)) {
                this.value = ""
            } else if (parseInt(this.value) > 15) {
                this.value = ""
            }
        }

        let green_score_input = document.createElement('input')
        green_score_input.type = "text"
        green_score_input.placeholder = "Green Score"
        green_score_input.id = "green_score_input"
        green_score_input.onkeyup = function(event) {
            // check if it is a number
            if (isNaN(this.value)) {
                this.value = ""
            } else if (parseInt(this.value) > 15) {
                this.value = ""
            }

            if (event.code == 13) {
                if (red_score_input.value != "" && green_score_input.value != "") {
                    push_score(match_id, red_score_input.value, green_score_input.value)
                }
            }
        }
        
        let push_score_button = document.createElement('div')
        push_score_button.innerHTML = '<i class="fa-solid fa-paper-plane"></i>'
        push_score_button.onclick = function() {
            if (red_score_input.value != "" && green_score_input.value != "") {
                push_score(match_id, red_score_input.value, green_score_input.value)
            }
        }

        score_options.appendChild(red_score_input)
        score_options.appendChild(green_score_input)
        score_options.appendChild(push_score_button)

        score_options.style.animation = "fade-in " + panelAnimationTime + "ms ease-in-out"

        parentElement.insertBefore(score_options, siblingElement.nextSibling)
    });
}


function push_score(id, green_score, red_score) {
    
    const data = new URLSearchParams();
    data.append('id', id);
    data.append('green_score', green_score);
    data.append('red_score', red_score);

    fetch('matches/push_score', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        if(data.success == false) {
            alert(data.message)
        }
    })
    .then(data => {
        get_matches()
        // if window is an iframe, send message to parent window
        if (window.parent !== window) {
            let reciever_iframe = window.parent.document.getElementById("standings_frame");
            // Send the message to the "standings_frame" iframe, allowing the message to be sent to any origin
            reciever_iframe.contentWindow.postMessage("should_update_standings", "*");
        }
    })
}

function match_set_active(id) {
    // check if a match on the same piste is already active
    const all_matches = document.getElementsByClassName("item")
    for (const element of all_matches) {
        if (element.dataset.ongoing == "true") {
            if (element.children[1].children[0].innerHTML === document.getElementById("match-" + id).children[1].children[0].innerHTML) {
                // ask the user if they want to continue
                if (confirm("A match on the same piste is already ongoing. Do you want to continue?\n\nContinuing here is an EXPERIMENTAL FEATURE that could cause fatal bugs and disrupt the ongoing tournament.") == false) {
                    return;
                }
                if (confirm("Are you sure you want to set the match active?") == false) {
                    return;
                } else {
                    break;
                }
            }
        }
    }

    // send JSON to server (POST)
    let data = {}
    data["id"] = id
    fetch('matches/set_active', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            get_matches()
        } else {
            alert("A match on the same piste is already ongoing")
        }
    })
    .catch(error => {
        console.log(error)
    })
}

function prioritize_match(id, value) {
    // send JSON to server (POST)
    let data = {}
    data["id"] = id
    data["value"] = value
    fetch('matches/prioritize', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === false) {
            alert(data.message)
        } else {
            get_matches()
        }
    })
}

function assign_piste(match_id, piste) {
    // send JSON to server (POST)
    let data = {}
    data["id"] = match_id
    data["piste"] = piste
    fetch('matches/assign_piste', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === false) {
            alert(data.message)
        } else {
            get_matches()
        }
    })
}

function remove_piste_assignment(match_id) {
    // send JSON to server (POST)
    let data = {}
    data["id"] = match_id
    fetch('matches/remove_piste_assignment', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === false) {
            alert(data.message)
        } else {
            get_matches()
        }
    })
}




function open_in_new_tab() {
    window.open("matches", "_blank")
}

let filter_toggle = false;
function toggleFilter(just_apply = false) {
    if (just_apply === false) {
        filter_toggle = !filter_toggle;
        if (filter_toggle === true) {
            document.getElementById("filter").className = "fa-solid fa-filter-circle-xmark"
        } else {
            document.getElementById("filter").className = "fa-solid fa-filter"
        }
    }

    for (const element of document.getElementsByClassName("item")) {
        if (element.dataset.completed == "true" && filter_toggle === true) {
            element.style.display = "none";
        } else {
            element.style.display = "contents";
        }
    }
}

window.onload = function() {
    // if not an iframe, update the matches
    if (window.self === window.top) {
        document.getElementById("open_in_new_tab").style.display = "none"
        get_matches()
    }
}

// Listen for messages from the parent window
window.addEventListener('message', function(event) {
    // Check if the message is 'callFunction'
    if (event.data === 'update') {
      // Call the function
      get_matches();
    }
});

function savePDF() {
    header = document.getElementById("header")
    header.style.display = "none"
    window.print()
    header.style.display = "flex"
}


window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};