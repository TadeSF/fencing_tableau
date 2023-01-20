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

async function add_header_flag(country) {
    if (country.length == 3) {
        let flag = document.getElementById("Main-Flag")
        flag.innerHTML = "";
        let svg = await parse_flag(country);
        flag.appendChild(svg);
    }
}

async function parse_flag(country) {
    if (country.length == 3) {
        let svgString = await get_flag(country);
        let parser = new DOMParser();
        let doc = parser.parseFromString(svgString, 'image/svg+xml');
        let svg = doc.querySelector('svg');
        return svg
    }
}

async function update() {
    let url = window.location.href;
    fetch(url + '/update')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        add_header_flag(data["nationality"]);

        document.getElementById("Current_Standing").innerHTML = data["current_rank"];
        if (data["current_group_rank"] != null) {
            document.getElementById("Group-Standing-Block").style.display = "block";
            document.getElementById("Group_Standing").innerHTML = data["current_group_rank"];
        } else {
            document.getElementById("Group-Standing-Block").style.display = "none";
        }

        document.getElementById("Group_Number").innerHTML = data["group"];

        let streak_wrapper = document.getElementById("Streak");
        if (data["outcome_last_matches"].length > 0) {
            streak_wrapper.innerHTML = "";
        }
        for (const element of data["outcome_last_matches"]) {
            let box = document.createElement("div");
            box.className = "Streak-Block";
            if (element == true) {
                box.style.backgroundColor = "green";
                box.style.color = "white";
                box.innerHTML = "W";
            } else if (element == false) {
                box.style.backgroundColor = "red";
                box.style.color = "white";
                box.innerHTML = "L";
            }
            streak_wrapper.appendChild(box);
        }

        let next_match = data["next_matches"][0];
        if (next_match != null) {
            // if the length of next_matches is 1, then hide the "Next-Opponents" section
            if (data["next_matches"].length == 1) {
                document.getElementById("Next-Match-Section").style.display = "block";
                document.getElementById("Next-Opponents").style.display = "none";    
                document.getElementById("No-More-Matches").style.display = "none";
            } else {
                document.getElementById("Next-Match-Section").style.display = "block";
                document.getElementById("Next-Opponents").style.display = "block";    
                document.getElementById("No-More-Matches").style.display = "none";
            }

            document.getElementById("Next-Piste-Number").innerHTML = next_match["piste"];
            
            let opponent_fencer_box = document.getElementById("Next-Match-Fencer")

            let opponent = next_match["opponent"];
            parse_flag(opponent["nationality"]).then((value) => {
                let svg;
                svg = value;
                let flag = document.createElement("div");
                flag.appendChild(svg);
                flag.className = "Next-Match-Flag";
                let fencer_name = document.createElement("div");
                fencer_name.innerHTML = opponent["name"] + " " + "(" + opponent["club"] + ")";
                opponent_fencer_box.innerHTML = "";
                opponent_fencer_box.appendChild(flag);
                opponent_fencer_box.appendChild(fencer_name);
            });

            let opponent_wrapper = document.getElementById("Opponents-Wrapper");
            opponent_wrapper.innerHTML = "";
            for (const element of data["next_matches"]) {
                // if the index is 0, then it is the next match, so skip it
                if (data["next_matches"].indexOf(element) == 0) {
                    continue;
                }
                let opponent = document.createElement("div");
                opponent.className = "Fencer-Banner";
                let opponent_flag = document.createElement("div");
                opponent_flag.className = "Next-Match-Flag";
                let opponent_name = document.createElement("div");
                opponent_name.className = "Fencer-Name";
                opponent_name.innerHTML = element["opponent"]["name"] + " " + "(" + element["opponent"]["club"] + ")";
                parse_flag(element["opponent"]["nationality"]).then((value) => {
                    let svg;
                    svg = value;
                    opponent_flag.appendChild(svg);
                });
                opponent.appendChild(opponent_flag);
                opponent.appendChild(opponent_name);
                opponent_wrapper.appendChild(opponent);
            }


            let piste_helper = document.getElementById("piste_helper");

            if (next_match["piste"] === "TBA") {
                document.getElementById("Next-Piste-Block").style.backgroundColor = "yellow";
                document.getElementById("Next-Piste-Title").innerHTML = "Upcoming Match";
                document.getElementById("Next-Piste-Block").style.color = "black";
                piste_helper.innerHTML = "The piste number will be announced later.<br>Come back regularly to check the piste number.";
            } else if (next_match["ongoing"] === true) {
                if (next_match["color"] === "green") {
                    document.getElementById("Next-Piste-Block").style.backgroundColor = "green";
                } else if (next_match["color"] === "red") {
                    document.getElementById("Next-Piste-Block").style.backgroundColor = "red";
                }
                document.getElementById("Next-Piste-Block").style.color = "white";
                document.getElementById("Next-Piste-Title").innerHTML = "Ongoing Match";
                piste_helper.innerHTML = "The match is ongoing.<br>You are fencing on this piste right now.<br>The color of the piste indicates your color.";
            } else {
                document.getElementById("Next-Piste-Title").innerHTML = "Upcoming Match";
                document.getElementById("Next-Piste-Block").style.color = "black";
                piste_helper.innerHTML = "You are fencing on this piste next, but there is still another match ongoing.<br>Please stand by and get ready."
                // flashing the background color in white and yellow
                let color = "white";
                let color1 = "white";
                let color2 = "orange";
                let text_color = "black";
                let text_color1 = "black";
                let text_color2 = "black";
                if (next_match["piste_occupied"] === false) {
                    if (next_match["color"] === "green") {
                        color1 = "green";
                        color2 = "white";
                        text_color1 = "white";
                        text_color2 = "black";
                    } else if (next_match["color"] === "red") {
                        color1 = "red";
                        color2 = "white";
                        text_color1 = "white";
                        text_color2 = "black";
                    }
                    piste_helper.innerHTML = "You are fencing on this piste next.<br>The previous match has finished.<br>The color of the piste indicates your color.";
                }
                let interval = setInterval(function() {
                    document.getElementById("Next-Piste-Block").style.backgroundColor = color;
                    document.getElementById("Next-Piste-Block").style.color = text_color
                    color = (color == color1) ? color2 : color1;
                    text_color = (text_color == text_color1) ? text_color2 : text_color1;
                }, 1000);
                setTimeout(function() {clearInterval(interval)}, 10000);
            }
        } else {
            document.getElementById("Next-Match-Section").style.display = "none";
            document.getElementById("Next-Opponents").style.display = "none";
            document.getElementById("No-More-Matches").style.display = "block";
        }
    });

}


window.onload = function() {
    update();

    // Wait for 2 seconds
    // setTimeout(function() {update()}, 1000);
}

// Update every 10 seconds
setInterval(function() {update()}, 10000);



function standings(content) {
    let group;
    if (content === "all") {
        group = "all";
    } else if (content === "group") {
        group = document.getElementById("Group_Number").innerHTML;
    }

    window.open("standings/" + group, "_blank");

}

document.querySelector("#Next-Piste-Block").addEventListener("click", (event) => {
    let pisteHelper = document.querySelector(".piste_helper");
    pisteHelper.classList.toggle("hide");
});