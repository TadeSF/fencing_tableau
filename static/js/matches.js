window.location = "matches.html"

// Get the width and height of the screen
const screenWidth = window.screen.width;
const screenHeight = window.screen.height;

// Calculate the width and height of the window
const windowWidth = Math.round(screenWidth * 0.6);
const windowHeight = Math.round(screenHeight * 0.6);

// Calculate the top and left position of the window
const windowTop = screenHeight - windowHeight;
const windowLeft = 0;

// Resize and move the window
window.resizeTo(windowWidth, windowHeight);
window.moveTo(windowLeft, windowTop);




function update_matches(matches, stage) {
    let matches_table = document.getElementById('matches_table')

    // Change stage headline
    let stage_item = document.getElementById('stage')
    stage_item.innerHTML = stage

    // Remove all rows from the table

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
        let group_text = document.createTextNode(element["group"])
        let piste_text = document.createTextNode(element["piste"])
        let score_text = document.createTextNode(element["green_score"] + " : " + element["red_score"])
        let button_text = document.createTextNode("Input Score")
        
        
        let green_fencer_text = document.createTextNode(element["green"])
        let green_fencer_div = document.createElement('div')
        let green_flag = document.createElement('div')
        green_flag.className = "flag"
        green_fencer_div.classList.add("fencer-div-green")
        green_fencer_div.classList.add("fencer-div")
        green_flag.innerHTML = element["green_flag"]
        green_flag.querySelector("svg").style.width = "20px"
        green_fencer_div.appendChild(green_flag)
        green_fencer_div.appendChild(green_fencer_text)
        green_fencer.appendChild(green_fencer_div)
        
        let red_fencer_text = document.createTextNode(element["red"])
        let red_fencer_div = document.createElement('div')
        let red_flag = document.createElement('div')
        red_flag.className = "flag"
        red_fencer_div.classList.add("fencer-div-red")
        red_fencer_div.classList.add("fencer-div")
        red_flag.innerHTML = element["red_flag"]
        red_flag.querySelector("svg").style.width = "20px"
        red_fencer_div.appendChild(red_flag)
        red_fencer_div.appendChild(red_fencer_text)
        red_fencer.appendChild(red_fencer_div)

        
        id.appendChild(id_text)
        group.appendChild(group_text)
        piste.appendChild(piste_text)
        score.appendChild(score_text)
        button.appendChild(button_text)

        // make the button clickable
        button.className = "cell-button"
        button.onclick = function() {
            eel.input_score(this.parentNode.childNodes[0].innerHTML)
        }

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

eel.expose(update_matches)