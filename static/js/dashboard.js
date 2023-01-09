window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
  };

function update() {
    fetch('dashboard/update')
    .then(response => response.json())
    .then(response => {
        document.getElementById("main_id_text").innerHTML = response["id"]
        document.getElementById("Tournament_Name").innerHTML = response["name"]
        document.getElementById("Tournament_Location").innerHTML = response["location"]
        document.getElementById("Tournament_Stage").innerHTML = response["stage"]
        document.getElementById("elimination_mode").innerHTML = "Elimination Mode:<br>" + response["elimination_mode"]

        document.getElementById("num_fencers").innerHTML = response["num_fencers"]
        document.getElementById("num_clubs").innerHTML = response["num_clubs"]
        document.getElementById("num_prelim_groups").innerHTML = response["num_prelim_groups"]
        document.getElementById("num_prelim_rounds").innerHTML = response["num_prelim_rounds"]
        document.getElementById("first_elimination_round").innerHTML = response["first_elimination_round"]
        document.getElementById("num_wildcards").innerHTML = response["num_wildcards"]
        document.getElementById("num_pistes").innerHTML = response["num_pistes"]
        document.getElementById("num_matches").innerHTML = response["num_matches"]
        document.getElementById("num_matches_completed").innerHTML = response["num_matches_completed"]
        

        // Update the "Matches" table
        var iframe1 = document.getElementById('matches_frame');
        var iframeWindow1 = iframe1.contentWindow; // Get a reference to the window object of the iframe
        iframeWindow1.postMessage('update', '*'); // Send a message to the iframe

        // Update the "Standings" table
        var iframe2 = document.getElementById('standings_frame');
        var iframeWindow2 = iframe2.contentWindow; // Get a reference to the window object of the iframe
        iframeWindow2.postMessage('update', '*'); // Send a message to the iframe
    })
}

window.onload = function() {
    // Wait for 2 seconds
    setTimeout(function() {update()}, 1000);
}

function advance() {
    fetch('matches-left')
    .then(response => response.text())
    .then(response => {
        if (response === "0") {
            fetch('next-stage')
            .then(response => {
                if (response.status === 200) {
                    setTimeout(function() {update()}, 1000);
                }
            })
        } else {
            alert("There are still matches left to be completed!")
        }
    })
}