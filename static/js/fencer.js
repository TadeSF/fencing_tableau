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
        // Load the SVG string from the server
        let svgString = await get_flag(country);

        // Parse the SVG string into a DocumentFragment
        let parser = new DOMParser();
        let doc = parser.parseFromString(svgString, 'image/svg+xml');
        let svg = doc.querySelector('svg');

        // Append the DocumentFragment to the flag element
        flag.appendChild(svg);
    }
}

function update() {
    url = window.location.href;
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

        let streak_wrapper = document.getElementById("Streak");
        if (data["outcome_last_matches"].length > 0) {
            streak_wrapper.innerHTML = "";
        }
        for (let i = 0; i < data["outcome_last_matches"].length; i++) {
            let box = document.createElement("div");
            box.className = "Streak-Block";
            if (data["outcome_last_matches"][i] == true) {
                box.style.backgroundColor = "green";
                box.style.color = "white";
                box.innerHTML = "W";
            } else if (data["outcome_last_matches"][i] == false) {
                box.style.backgroundColor = "red";
                box.style.color = "white";
                box.innerHTML = "L";
            }
            streak_wrapper.appendChild(box);
        }
    });

}


window.onload = function() {
    update();

    // Wait for 2 seconds
    // setTimeout(function() {update()}, 1000);
}