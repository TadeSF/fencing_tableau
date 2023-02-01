// import { jsPDF } from "jspdf";

function get_matches() {
    fetch('matches/update')
    .then(response => response.json())
    .then(response => {
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

function clearTable(table) {
    // Get the first row (the row that contains the headers)
    var firstRow = table.rows[0];

    // Clear the table, starting from the second row (the first row is the row that contains the headers)
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }
}

function parseSVG(svgString) {
    // Parse the SVG string into a DocumentFragment
    let parser = new DOMParser();
    let doc = parser.parseFromString(svgString, 'image/svg+xml');
    let svg = doc.querySelector('svg');
    return svg;
}

async function update_matches(matches) {
    let matches_table = document.getElementById('matches_table')

    // Remove all rows from the table

    clearTable(matches_table);

    // Add the new, updated rows
    for (const element of matches) {
        let row = document.createElement('tr')
        let id = document.createElement('td')
        let group = document.createElement('td')
        let piste = document.createElement('td')
        let score = document.createElement('td')
        let button = document.createElement('td')

        let green_fencer = document.createElement('td')
        let red_fencer = document.createElement('td')

        let id_text = document.createTextNode(element["id"])

        let group_text = "X"
        if (element["group"] != null) {
            group_text = document.createTextNode(element["group"])
        } else {
            group_text = document.createTextNode("F")
        }

        let piste_text = "X"
        if (element["piste"] != null) {
            piste_text = document.createTextNode(element["piste"])
        } else {
            piste_text = document.createTextNode("-")
        }

        let score_text = document.createTextNode("- : -")
        if (element["green_score"] != 0 || element["red_score"] != 0) {
            score_text = document.createTextNode(element["green_score"] + " : " + element["red_score"])
        }

        let button_text = document.createTextNode("X")
        button.appendChild(button_text)
        button.className = "cell_button"
        button.id = "button_" + element["id"]
        if (element["ongoing"] == true) {
            button.innerHTML = "Ongoing"
            button.classList.add("cell_button-ongoing")
            button.onmouseover = function() {
                this.innerHTML = "Input Score"
            }
            button.onmouseout = function() {
                this.innerHTML = "Ongoing"
            }
            button.onclick = function() {
                openPromptWindow(this.parentNode.childNodes[0].innerHTML)
            }

        } else if (element["ongoing"] == false && element["complete"] == false) {
            button.innerHTML = "Not Started"
            button.classList.add("cell_button-start")
            button.onmouseover = function() {
                this.innerHTML = "Start Match"
            }
            button.onmouseout = function() {
                this.innerHTML = "Not Started"
            }
            button.onclick = function() {
                match_set_active(this.parentNode.childNodes[0].innerHTML)
            }

        } else if (element["ongoing"] == false && element["complete"] == true) {
            button.innerHTML = "Completed"
            button.classList.add("cell_button-finished")
            button.onmouseover = function() {
                this.innerHTML = "Correct Score"
            }
            button.onmouseout = function() {
                this.innerHTML = "Completed"
            }
            button.style.backgroundColor.hover = "red"
            button.onclick = function() {
                openPromptWindow(this.parentNode.childNodes[0].innerHTML)
            }
        } else {
            button.innerHTML = "Y"
        }
        
        
        let green_fencer_text = document.createTextNode(element["green"])
        let green_fencer_div = document.createElement('div')
        let green_flag = document.createElement('div')
        green_flag.className = "flag"
        let green_svgString = await get_flag(element["green_nationality"]);
        let green_svg = parseSVG(green_svgString)
        green_flag.appendChild(green_svg); // Add the green_svg element to green_flag
        green_fencer_div.classList.add("fencer-div-green")
        green_fencer_div.classList.add("fencer-div")
        green_fencer_div.appendChild(green_fencer_text)
        green_fencer_div.appendChild(green_flag)
        green_fencer.appendChild(green_fencer_div)
        
        let red_fencer_text = document.createTextNode(element["red"])
        let red_fencer_div = document.createElement('div')
        let red_flag = document.createElement('div')
        red_flag.className = "flag"
        let red_svgString = await get_flag(element["red_nationality"]);
        let red_svg = parseSVG(red_svgString)
        red_flag.appendChild(red_svg); // Add the red_svg element to red_flag
        red_fencer_div.classList.add("fencer-div-red")
        red_fencer_div.classList.add("fencer-div")
        red_fencer_div.appendChild(red_flag)
        red_fencer_div.appendChild(red_fencer_text)
        red_fencer.appendChild(red_fencer_div)

        
        id.appendChild(id_text)
        group.appendChild(group_text)
        piste.appendChild(piste_text)
        score.appendChild(score_text)

        

        id.className = "cell-id"


        row.appendChild(id)
        row.appendChild(group)
        row.appendChild(piste)
        row.appendChild(green_fencer)
        row.appendChild(score)
        row.appendChild(red_fencer)
        row.appendChild(button)

        matches_table.appendChild(row)
    }
}


function openPromptWindow(id) {
    const prompt = document.getElementById('prompt');
    prompt.style.display = 'block';
    document.getElementById('form_id').value = id;
    let green_fencer = document.getElementById('form_greenScore')
    green_fencer.placeholder = document.getElementById('button_' + id).parentNode.childNodes[3].textContent.trim();
    let red_fencer = document.getElementById('form_redScore')
    red_fencer.placeholder = document.getElementById('button_' + id).parentNode.childNodes[5].textContent.trim();
}

function closePromptWindow() {
    const prompt = document.getElementById('prompt');
    prompt.style.display = 'none';
    document.getElementById('form_id').value = "";
    document.getElementById('form_greenScore').value = "";
    document.getElementById('form_redScore').value = "";
};


const form = document.getElementById('form');
form.addEventListener('submit', (event) => {
    event.preventDefault(); // prevent the form from reloading the page

    // get the values of the form inputs
    const id = document.getElementById('form_id').value;
    const greenScore = document.getElementById('form_greenScore').value;
    const redScore = document.getElementById('form_redScore').value;

    // do something with the form values (e.g. send them to a server)
    push_score(id, greenScore, redScore);

    // clear the form
    document.getElementById('form_id').value = "";
    document.getElementById('form_greenScore').value = "";
    document.getElementById('form_redScore').value = "";
    document.getElementById('prompt').style.display = "none";


    // change the button
    let button = document.getElementById("button_" + id)
    button.classList.add("cell_button-finished")
        button.classList.remove("cell_button-ongoing")
    button.onclick = function() {
        alert("Match already finished")
    }
    button.innerHTML = "Completed"


});


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
            let button = document.getElementById("button_" + id)
            button.innerHTML = "Ongoing"
            button.classList.add("cell_button-ongoing")
            button.classList.remove("cell_button-start")
            button.onclick = function() {
                openPromptWindow(this.parentNode.childNodes[0].innerHTML)
            }
            button.onmouseover = function() {
                this.innerHTML = "Input Score"
            }
            button.onmouseout = function() {
                this.innerHTML = "Ongoing"
            }
        } else {
            alert("A match on the same piste is already ongoing")
        }
    })
    .catch(error => {
        console.log(error)
    })
}

function open_in_new_tab() {
    window.open("matches", "_blank")
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