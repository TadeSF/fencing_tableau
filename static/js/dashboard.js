const tournament_id = document.getElementById("body").dataset.tournament;

window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
  };

function update() {
    fetch('dashboard/update')
    .then(response => response.json())
    .then(response => {
        document.getElementById("main_id_text").innerHTML = response["id"]
        document.getElementById("main_id_text_pw").innerHTML = response["id"]
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
            if (response.status === 404) {
                alert("The Tournament does not exist!")
            } else {
                alert("There are still matches left to be completed!")
            }
        }
    })
}

function simulate() {
    document.getElementById("loading-screen").style.display = "flex";
    fetch('simulate-current')
    .then(response => {
        if (response.status === 200) {
            setTimeout(function() {
                update();
                document.getElementById("loading-screen").style.display = "none";
        }, 1000);
        } else {
            alert("There are no matches left to be simulated!")
            document.getElementById("loading-screen").style.display = "none";
        }
    })
}

async function checkLogin() {
    let response = await fetch('dashboard/check-login');
    let responseText = await response.text();
    let parsedResponse = JSON.parse(responseText);
    return parsedResponse.success;
}

window.addEventListener('load', function() {
    setTimeout(function() {
      document.getElementById('loading-screen').style.display = 'none';
    }, 1000);
  });


window.onload = async function() {
    // Wait for 2 seconds
    let loginStatus = await checkLogin();
    if (loginStatus == false) {
      document.getElementById("login-overlay").style.display = "block";
    } else {
      document.getElementById("login-overlay").style.display = "none";
    }
    setTimeout(function() {update()}, 1000);
};
  
// overlay-form submit
document.getElementById("overlay-form").addEventListener("submit", function(event) {
    event.preventDefault();
    let password = document.getElementById("password-input").value;
    let tournament_id = document.getElementById("main_id_text").innerHTML;
    let data = {
        tournament: tournament_id,
        password: password
    };
    let response = fetch("/master-login", {
        method: "POST",
        body: JSON.stringify(data), 
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        if (response.status === 200) {
            document.getElementById("login-overlay").style.display = "none";
        } else {
            alert("Invalid username or password!");
        }
    });
});

function openTableau() {
    window.open("/" + tournament_id + "/tableau?group=1", "_blank");
}