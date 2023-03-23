const tournament_id = document.getElementById("body").dataset.tournament;

window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
  };

function update(update_iframes=true) {
    fetch('/api/dashboard/update?tournament_id=' + tournament_id)
        .then(response => response.json())
        .then(response => {
            if (Object.keys(response).includes("error")) {
                console.log(response["error"]);
                alert_string = "Error: " + response["error"]["code"];
                if (response["error"]["message"]) {
                    alert_string += "\n\n" + response["error"]["message"];
                }
                alert_string += "\n Do you want to view the logs?";
                if (response["error"]["exception"]) {
                    alert_string += "\n\n" + response["error"]["exception"];
                }
                var result = window.confirm(alert_string);
                if (result == true) {
                    window.open("/logs", "_blank");
                }
            } else {
                document.getElementById("main_id_text").innerHTML = response["id"]
                document.getElementById("main_id_text_pw").innerHTML = response["id"]
                document.getElementById("Tournament_Name").innerHTML = response["name"]
                document.getElementById("Tournament_Location").innerHTML = response["location"]
                document.getElementById("Tournament_Stage").innerHTML = response["stage"]
                document.getElementById("elimination_mode").innerHTML = response["elimination_mode"]

                document.getElementById("num_fencers").innerHTML = response["num_fencers"]
                document.getElementById("num_clubs").innerHTML = response["num_clubs"]
                document.getElementById("num_nationalities").innerHTML = response["num_nationalities"]
                document.getElementById("num_prelim_groups").innerHTML = response["num_prelim_groups"]
                document.getElementById("num_prelim_rounds").innerHTML = response["num_prelim_rounds"]
                document.getElementById("first_elimination_round").innerHTML = response["first_elimination_round"]
                document.getElementById("num_wildcards").innerHTML = response["num_wildcards"]
                document.getElementById("num_pistes").innerHTML = response["num_pistes"]
                document.getElementById("num_matches").innerHTML = response["num_matches"]
                document.getElementById("num_matches_completed").innerHTML = response["num_matches_completed"]

                // If all matches of the current stage are completed, show the "Advance" button
                if (parseInt(response["num_matches"]) - parseInt(response["num_matches_completed"]) == 0) {
                    document.getElementById("Advance").style.display = "block";
                } else {
                    document.getElementById("Advance").style.display = "none";
                }
            
                if (update_iframes === true) {
                    // Update the "Matches" table
                    let iframe1 = document.getElementById('matches_frame');
                    let iframeWindow1 = iframe1.contentWindow; // Get a reference to the window object of the iframe
                    iframeWindow1.postMessage('update', '*'); // Send a message to the iframe
                }

                // Update the "Standings" table
                let iframe2 = document.getElementById('standings_frame');
                let iframeWindow2 = iframe2.contentWindow; // Get a reference to the window object of the iframe
                iframeWindow2.postMessage('update', '*'); // Send a message to the iframe

                // if Stage does not contain Preliminary Round (it always has a number afterwards), hide the "Tableau" button 
                if (response["stage"].split(" ")[0] !== "Preliminary") {
                    document.getElementById("Tableau").style.display = "none";
                    document.getElementById("Brackets").style.display = "block";
                } else {
                    document.getElementById("Tableau").style.display = "block";
                    document.getElementById("Brackets").style.display = "none";
                }

                if (response["stage"] === "Finished") {
                    document.getElementById("Simulate").style.display = "none";
                    document.getElementById("Advance").style.display = "none";
                    document.getElementById("Results").style.display = "block";
                }

                // if Simulation is disabled, hide the "Simulate" button
                if (response["simulation_active"] === false) {
                    document.getElementById("Simulate").style.display = "none";
                }
            }
    })
}

function advance() {
    const advance_button = document.getElementById("Advance");
    advance_button.disabled = true;
    advance_button.firstChild.classList.remove("fa-forward-fast");
    advance_button.firstChild.classList.add("fa-spin");
    advance_button.firstChild.classList.add("fa-spinner");

    fetch('/api/matches/matches-left?tournament_id=' + tournament_id)
        .then(response => response.json())
        .then(response => {
            if (response.matches_left == "0") {
                fetch('/api/next-stage?tournament_id=' + tournament_id)
                .then(response => {
                    if (response.status === 200) {
                        setTimeout(function() {update()}, 1000);
                    } else {
                        console.log(response)
                        alert("An error occurred!")
                    }
                })
            } else {
                if (response.status === 404) {
                    alert("The Tournament does not exist!")
                } else {
                    alert("There are still matches left to be completed!")
                }
                console.log(response)
            }

            setTimeout(function() {
                advance_button.disabled = false;
                advance_button.firstChild.classList.remove("fa-spin");
                advance_button.firstChild.classList.remove("fa-spinner");
                advance_button.firstChild.classList.add("fa-forward-fast");
            }, 1500);
    })

    
}

function simulate() {
    const simulate_button = document.getElementById("Simulate");
    simulate_button.disabled = true;
    simulate_button.firstChild.classList.remove("fa-gears");
    simulate_button.firstChild.classList.add("fa-spin");
    simulate_button.firstChild.classList.add("fa-spinner");

    let confirm = window.confirm("Are you sure you want to simulate this stage of the tournament?");
    if (confirm) {
        fetch('/api/simulate?tournament_id=' + tournament_id)
        .then(response => {
            if (response.status === 200) {
                setTimeout(function() {
                    update();
                }, 1000);
            } else {
                alert("There are no matches left to be simulated!")
            }

            setTimeout(function() {
                simulate_button.disabled = false;
                simulate_button.firstChild.classList.remove("fa-spin");
                simulate_button.firstChild.classList.remove("fa-spinner");
                simulate_button.firstChild.classList.add("fa-gears");
            }, 1500);
        });
    } else {
        setTimeout(function() {
            simulate_button.disabled = false;
            simulate_button.firstChild.classList.remove("fa-spin");
            simulate_button.firstChild.classList.remove("fa-spinner");
            simulate_button.firstChild.classList.add("fa-gears");
        }, 1500);
    }
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
    setTimeout(function () {
        update();
    }, 2000);
    
    setInterval(function () {
        update(update_iframes = false);
    }, 5000);
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

function openBrackets() {
    window.open("/" + tournament_id + "/brackets", "_blank");
}

function openQR() {
    // open a new window (width 500px, heigth 800px) with a QR Code for the path /fencer-login?tournament=<tournament_id>
    window.open("/qr/fencer?tournament_id=" + tournament_id, "_blank", "width=400,height=480");
}

function copyID() {
    let id = document.getElementById("main_id_text").innerHTML;
    console.log(id);
    navigator.clipboard.writeText(id);
    alert('Copied ID "' + id + '" to clipboard!');
}

function pistes() {
    window.open("/" + tournament_id + "/piste-overview", "_blank");
}

function disqualify() {
    document.getElementById("disqualify-overlay").style.display = "flex";
}

// Event listener for closing disqualify overlay. When clicked outside of the overlay, it will close.
document.getElementById("disqualify-overlay").addEventListener("click", function (event) {
    if (event.target == document.getElementById("disqualify-overlay")) {
        closeOverlay();
    }
});

function download_results() {
    const results_button = document.getElementById("Results");
    results_button.disabled = true;
    results_button.firstChild.classList.remove("fa-download");
    results_button.firstChild.classList.add("fa-spin");
    results_button.firstChild.classList.add("fa-spinner");

    window.open("/api/download-results?tournament_id=" + tournament_id, "_blank");

    setTimeout(function() {
        results_button.disabled = false;
        results_button.firstChild.classList.remove("fa-spin");
        results_button.firstChild.classList.remove("fa-spinner");
        results_button.firstChild.classList.add("fa-check");
    }, 1500);

    setTimeout(function() {
        results_button.firstChild.classList.remove("fa-check");
        results_button.firstChild.classList.add("fa-download");
    }, 3000);
}

// listen for iframe message "should_update_dashboard" and update dashboard
window.addEventListener("message", function (event) {
    if (event.data === "should_update_dashboard") {
        console.log("Received message from iframe, updating dashboard...")
        update();
    }
});




// Disqualify overlay

// Get overlay and close button elements
const overlay = document.getElementById("disqualify-overlay");
const closeButton = document.querySelector(".close");

// Get form and input elements
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const searchResults = document.getElementById("search-results");

const disqualifyForm = document.getElementById("disqualify-form");
const confirmCheckbox = document.getElementById("confirm-checkbox");
const disqualifyButton = document.getElementById("disqualify-button");

// Add event listener to open overlay when disqualify button is clicked
disqualifyButton.addEventListener("click", (event) => {
    event.preventDefault();
    disqualifyFencer();
});

// Add event listener to close overlay when close button is clicked
closeButton.addEventListener("click", (event) => {
    event.preventDefault();
    closeOverlay();
});

// Add event listener to search button to perform search
searchButton.addEventListener("click", (event) => {
    event.preventDefault();
    searchFencer();
});

// Add event listener to search input to enable/disable search button
searchInput.addEventListener("input", (event) => {
    const inputValue = event.target.value.trim();
    searchButton.disabled = !inputValue;
});

// Add event listener to confirm checkbox to enable/disable disqualify button
confirmCheckbox.addEventListener("change", (event) => {
    disqualifyButton.disabled = !event.target.checked;
});

function disqualifyFencer() {
    const fencer_id = searchResults.dataset.fencer_id;
    const reason = document.getElementById("disqualify-reason").value;

    const url = `/api/fencer/disqualify?tournament_id=${tournament_id }&fencer_id=${ fencer_id }`;
    const options = {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            reason: reason
        })
    };

    fetch(url, options)
        .then(response => {
            if (response.ok) {
                closeOverlay();
            } else {
                throw new Error("Disqualification failed");
            }
        })
        .catch(error => {
            console.error(error);
            alert("Disqualification failed");
        });
}

function searchFencer() {
    const startNumber = parseInt(searchInput.value.trim());
    let name_query = searchInput.value.trim().replace(/\s/g, "%20");
    let url;

    if (isNaN(startNumber)) {
        url = `/api/fencer/disqualify?tournament_id=${tournament_id}&name=${name_query}`;
    } else {
        url = `/api/fencer/disqualify?tournament_id=${tournament_id}&start_number=${startNumber}`;
    }

    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Search failed");
            }
        })
        .then(data => {
            if (data.id) {
                displayFencer(data);
            } else {
                throw new Error("Fencer not found");
            }
        })
        .catch(error => {
            console.error(error);
            alert("Fencer not found");
        });
}

function displayFencer(fencer) {
    const fencerInfo = `
        <p>Fencer to disqualify found:</p>
        <p style="font-size: 1.3rem">${fencer.start_number}&emsp;<strong>${fencer.name}</strong> (${fencer.nationality}) – ${fencer.club}</p>
        <p>A disqualified Fencer is not removed from the tournament, but all remaining matches are automatically lost. The Fencer will be marked as disqualified in the results. There is currently no way to undo this action.</p>`;
    searchResults.innerHTML = fencerInfo;
    searchResults.dataset.fencer_id = fencer.id;
    disqualifyButton.disabled = !confirmCheckbox.checked;
}

function closeOverlay() {
    overlay.style.display = "none";
    searchInput.value = "";
    searchButton.disabled = true;
    searchResults.innerHTML = "";
    confirmCheckbox.checked = false;
    disqualifyButton.disabled = true;
}