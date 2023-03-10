const fencer_id = document.getElementById("body").dataset.fencer_id
const tournament_id = document.getElementById("body").dataset.tournament_id

let logged_in_fencer = false;
let logged_in_master = false;


// ---- Charts ----

const ctx = document.getElementById('Standings-Chart').getContext('2d');
const ctx2 = document.getElementById('Difference-Chart').getContext('2d');
const ctx3 = document.getElementById('Difference-Match-Chart').getContext('2d');

let StandingsChart;
let DifferenceChart;
let DifferenceMatchChart;

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
        let flag2 = document.getElementById("Information-Flag")
        flag.innerHTML = "";
        flag2.innerHTML = "";
        let svg = await parse_flag(country);
        flag.appendChild(svg);
        flag2.appendChild(svg.cloneNode(true));
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
    fetch('/api/fencer/update?tournament_id=' + tournament_id + '&fencer_id=' + fencer_id)
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
            let i = 1;
            let outcome_last_matches = data["outcome_last_matches"].slice(-5);
            console.log(outcome_last_matches);
            for (const element of outcome_last_matches) {
                if (i == 6) {
                    break;
                }
                let box = document.getElementById("Streak-" + i);
                if (element === true) {
                    box.style.backgroundColor = "green";
                    box.style.color = "white";
                    box.innerHTML = "W";
                } else if (element === false) {
                    box.style.backgroundColor = "red";
                    box.style.color = "white";
                    box.innerHTML = "L";
                }
                streak_wrapper.appendChild(box);
                i++;
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

                document.getElementById("Next-Match-Section").dataset.id = next_match["id"];

                if (next_match["piste"] != "TBA") {
                    document.getElementById("Next-Piste-Number").innerHTML = next_match["piste"];
                } else {
                    document.getElementById("Next-Piste-Number").innerHTML = '<i class="fa-solid fa-clock"></i>';
                }

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
                    opponent_fencer_box.onclick = function () {
                        window.open("/" + tournament_id + "/fencer/" + opponent["id"], "_blank")
                    }
                });

                let opponent_wrapper = document.getElementById("Opponents-Wrapper");
                opponent_wrapper.innerHTML = "";
                for (const element of data["next_matches"]) {
                    // if the index is 0, then it is the next match, so skip it
                    if (data["next_matches"].indexOf(element) == 0) {
                        continue;
                    }
                    let opponent = document.createElement("div");
                    opponent.className = "Fencer-Banner-Opponent";
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
                    opponent.onclick = function () {
                        window.open("/" + tournament_id + "/fencer/" + element["opponent"]["id"], "_blank")
                    }
                }


                const piste_helper = document.getElementById("piste_helper");
                const piste_block = document.getElementById("Next-Piste-Block");

                // remove all the classes from piste_block
                if (piste_block.classList.contains("piste-tba")) {
                    piste_block.classList.remove("piste-tba");
                }
                if (piste_block.classList.contains("piste-staged-red")) {
                    piste_block.classList.remove("piste-staged-red");
                }
                if (piste_block.classList.contains("piste-staged-green")) {
                    piste_block.classList.remove("piste-staged-green");
                }
                if (piste_block.classList.contains("piste-ongoing-red")) {
                    piste_block.classList.remove("piste-ongoing-red");
                }
                if (piste_block.classList.contains("piste-ongoing-green")) {
                    piste_block.classList.remove("piste-ongoing-green");
                }

                if (next_match["piste"] === "TBA") {
                    piste_block.classList.add("piste-tba");
                    document.getElementById("Next-Piste-Title").innerHTML = "Upcoming Match";
                    piste_helper.innerHTML = "The piste number will be announced later.<br>Come back regularly to check the piste number.";
                    document.getElementById("button_start_match").style.display = "none";
                    document.getElementById("button_input_score").style.display = "none";
                } else if (next_match["ongoing"] === true) {
                    if (next_match["color"] === "green") {
                        piste_block.classList.add("piste-ongoing-green");
                    } else if (next_match["color"] === "red") {
                        piste_block.classList.add("piste-ongoing-red");
                    }
                    document.getElementById("Next-Piste-Title").innerHTML = "Ongoing Match";
                    piste_helper.innerHTML = "The match is ongoing.<br>You are fencing on this piste right now.<br>The color of the piste indicates your color.";
                    if ((data["logged_in_as_fencer"] === true && data["allow_fencers_to_input_scores"] === true) || data["logged_in_as_master"] === true) {
                        document.getElementById("button_input_score").style.display = "flex";
                    } else {
                        document.getElementById("button_input_score").style.display = "none";
                    }
                    document.getElementById("button_start_match").style.display = "none";

                } else {
                    document.getElementById("Next-Piste-Title").innerHTML = "Upcoming Match";
                    piste_helper.innerHTML = "You are fencing on this piste next, but there is still another match ongoing.<br>Please stand by and get ready.";
                    if (next_match["color"] === "green") {
                        piste_block.classList.add("piste-staged-green");
                    } else if (next_match["color"] === "red") {
                        piste_block.classList.add("piste-staged-red");
                    }
                    piste_helper.innerHTML = "You are fencing on this piste next.<br>The previous match has finished.<br>The color of the piste indicates your color.";
                    if ((data["logged_in_as_fencer"] === true && data["allow_fencers_to_start_matches"] === true) || data["logged_in_as_master"] === true) {
                        document.getElementById("button_start_match").style.display = "flex";
                    } else {
                        document.getElementById("button_start_match").style.display = "none";
                    }
                    document.getElementById("button_input_score").style.display = "none";
                }
            } else {
                document.getElementById("Next-Match-Section").style.display = "none";
                document.getElementById("Next-Opponents").style.display = "none";
                document.getElementById("No-More-Matches").style.display = "block";
                if (data["group_stage"] == true) {
                    // document.getElementById("tableau-wrapper").style.display = "flex";
                    if (data["approved_tableau"] == false && logged_in_fencer == true) {
                        document.getElementById("approval-needed").style.display = "block";
                    } else {
                        document.getElementById("approval-needed").style.display = "none";
                    }
                } else {

                    // document.getElementById("tableau-wrapper").style.display = "none";
                    document.getElementById("approval-needed").style.display = "none";
                }
                document.getElementById("button_start_match").style.display = "none";
                document.getElementById("button_input_score").style.display = "none";
            }

            let tableau_button = document.getElementById("button_view_tableau");
            let tableau_finished_button = document.getElementById("button_finished_view_tableau");
            let brackets_button = document.getElementById("button_view_brackets");
            let brackets_finished_button = document.getElementById("button_finished_view_brackets");
            if (data["group_stage"] === true) {
                tableau_button.style.display = "block";
                tableau_finished_button.style.display = "block";
                brackets_button.style.display = "none";
                brackets_finished_button.style.display = "none";
            } else {
                tableau_button.style.display = "none";
                tableau_finished_button.style.display = "none";
                brackets_button.style.display = "block";
                brackets_finished_button.style.display = "block";
            }

            let statistics_matches = document.getElementById("Matches");
            let statistics_victories = document.getElementById("Victories");
            let statistics_defeats = document.getElementById("Defeats");
            let statistics_victory_rate = document.getElementById("Victory_Rate");
            let statistics_points = document.getElementById("Points_For");
            let statistics_points_against = document.getElementById("Points_Against");
            let statistics_points_difference = document.getElementById("Points_Difference");
            let statistics_points_per_match = document.getElementById("Points_per_Match");

            statistics_matches.innerHTML = data["statistics"]["overall"]["matches"];
            statistics_victories.innerHTML = data["statistics"]["overall"]["wins"];
            statistics_defeats.innerHTML = data["statistics"]["overall"]["losses"];
            statistics_victory_rate.innerHTML = data["win_percentage"];
            statistics_points.innerHTML = data["statistics"]["overall"]["points_for"];
            statistics_points_against.innerHTML = data["statistics"]["overall"]["points_against"];
            statistics_points_difference.innerHTML = data["points_difference"];
            statistics_points_per_match.innerHTML = data["points_per_match"];

            let information_gender = document.getElementById("Information_Gender");
            let information_handedness = document.getElementById("Information_Handedness");
            let information_age = document.getElementById("Information_Age");

            information_gender.innerHTML = data["gender"]
            information_handedness.innerHTML = data["handedness"]
            information_age.innerHTML = data["age"]

            let standing_chart_data = data["graph_data"]["standings"]["data"];
            let standing_chart_labels = data["graph_data"]["standings"]["labels"];

            let standings_chart_wrapper = document.getElementById("Standings-Chart-Wrapper");
            let difference_chart_wrapper = document.getElementById("Difference-Chart-Wrapper");
            let difference_match_chart_wrapper = document.getElementById("Difference-Match-Chart-Wrapper");
            let no_data = document.getElementById("No-Data");

            if (standing_chart_data.length < 2) {
                standings_chart_wrapper.style.display = "none";
                difference_chart_wrapper.style.display = "none";
                difference_match_chart_wrapper.style.display = "none";
                no_data.style.display = "block";
            } else {
                standings_chart_wrapper.style.display = "block";
                difference_chart_wrapper.style.display = "block";
                difference_match_chart_wrapper.style.display = "block";
                no_data.style.display = "none";
            }

            const lineTension = 0.4;

            if (StandingsChart) {
                StandingsChart.destroy();
            }
            if (DifferenceChart) {
                DifferenceChart.destroy();
            }
            if (DifferenceMatchChart) {
                DifferenceMatchChart.destroy();

            }


            document.getElementById("Standings-Chart").innerHTML = "";
            document.getElementById("Difference-Chart").innerHTML = "";
            document.getElementById("Difference-Match-Chart").innerHTML = "";

            StandingsChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: standing_chart_labels,
                    datasets: [
                        {
                            label: "Standings",
                            data: standing_chart_data,
                            backgroundColor: "#000000",
                            borderColor: "#000000",
                            borderWidth: 2,
                            yAxisID: "y1",
                            xAxisID: "x1",
                            lineTension: lineTension,
                            fill: {
                                target: "start",
                                above: function (context) {
                                    const chart = context.chart;
                                    const {ctx, chartArea, scales} = chart;

                                    const chartWidth = chartArea.right - chartArea.left;
                                    const chartHeight = chartArea.bottom - chartArea.top;

                                        let gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartHeight + chartArea.top);
                                        gradient.addColorStop(0, "rgba(0, 0, 255, 0.8)");
                                        gradient.addColorStop(1, "rgba(0, 0, 255, 0.05)");

                                    return gradient
                                },
                            }
                        }
                    ]
                },
                options: {
                    // responsive: false,
                    // maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: true,
                            text: "Standings History",
                        },
                    },
                    scales: {
                        y1: {
                            reverse: true,
                            min: 1,
                            max: data["graph_data"]["standings"]["y_max"],
                            // display: false
                        },
                        x1: {
                            grid: {
                                display: false
                            },
                        }
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return tooltipItem.yLabel;
                            }
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }  
            });

            let difference_chart_data = data["graph_data"]["points_difference"]["data"];
            let difference_chart_labels = data["graph_data"]["points_difference"]["labels"];
            // Remove the first element of the array, as it is not needed
            difference_chart_labels.shift();
            let difference_chart_per_match_data = data["graph_data"]["points_difference_per_match"]["data"];

            let width, height, gradient;
            function getgradient(ctx, chartArea, scales) {
                const chartWidth = chartArea.right - chartArea.left;
                const chartHeight = chartArea.bottom - chartArea.top;

                if (!width || width !== chartWidth || height !== chartHeight) {
                    const point_zero = scales.y1.getPixelForValue(0);
                    const point_zero_height = point_zero - chartArea.top;
                    let point_zero_percentage = point_zero_height / chartHeight;
                    if (point_zero_percentage > 1) {
                        point_zero_percentage = 1;
                    } else if (point_zero_percentage < 0) {
                        point_zero_percentage = 0;
                    }

                    width = chartWidth;
                    height = chartHeight;
                    gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartHeight + chartArea.top);
                    gradient.addColorStop(point_zero_percentage, "rgba(0, 150, 0, 0.5)");
                    gradient.addColorStop(point_zero_percentage, "rgba(255, 0, 0, 0.5)");
                }
                return gradient;
            }

            DifferenceChart = new Chart(ctx2, {
                data: {
                    labels: difference_chart_labels,
                    datasets: [
                        {
                            type: "line",
                            label: "Points Difference Development",
                            data: difference_chart_data,
                            // backgroundColor: "rgba(0, 150, 0, 0.2)",
                            backgroundColor: function (context) {
                                const chart = context.chart;
                                const {ctx, chartArea, scales} = chart;

                                if (!chartArea) {
                                    return null;
                                }
                                return getgradient(ctx, chartArea, scales);
                            },
                            borderColor: "#000000",
                            borderWidth: 2,
                            lineTension: lineTension,
                            fill: true,
                            xAxisID: "x1",
                            yAxisID: "y1",
                            pointBackgroundColor: "#000000"
                        },
                    ]
                },
                options: {
                    // responsive: false,
                    // maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: true,
                            text: "Points Difference Development",
                        },
                    },
                    scales: {
                        x1: {
                            grid: {
                                display: false
                            },
                        },
                        y1: {
                            grid: {
                                color: function(context) {
                                    if (context.tick.value == 0) {
                                        return "#000000";
                                    } else {
                                        return "#dddddd";
                                    }
                                },
                                lineWidth: function(context) {
                                    if (context.tick.value == 0) {
                                        return 2;
                                    } else {
                                        return 1;
                                    }
                                }
                            }, 
                        }
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return tooltipItem.yLabel;
                            }
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });

            // If all values are positive, the 0 line is the lowest value
            // If all values are negative, the 0 line is the highest value
            if (Math.min(...difference_chart_per_match_data) >= 0) {
                DifferenceChart.options.scales.y1.min = 0;
            } else if (Math.max(...difference_chart_per_match_data) <= 0) {
                DifferenceChart.options.scales.y1.max = 0;
            }

            

            let colors_for_difference_chart = [];
            for (let i = 0; i < difference_chart_per_match_data.length; i++) {
                if (difference_chart_per_match_data[i] < 0) {
                    colors_for_difference_chart[i] = "rgba(255, 0, 0, 0.5)";
                } else {
                    colors_for_difference_chart[i] = "rgba(0, 150, 0, 0.5)";
                }
            }

            if (DifferenceMatchChart) {
                DifferenceMatchChart.destroy();
            }

            DifferenceMatchChart = new Chart(ctx3, {
                data: {
                    labels: difference_chart_labels,
                    datasets: [
                        {
                            type: "bar",
                            label: "Points Difference per Match",
                            data: difference_chart_per_match_data,
                            backgroundColor: colors_for_difference_chart,
                            borderColor: "#000000",
                            borderWidth: 2,
                            yAxisID: "y1",
                            xAxisID: "x1",
                            borderRadius: 5,
                        }
                    ]
                },
                options: {
                    // responsive: false,
                    // maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: true,
                            text: "Points Difference per Match",
                        },
                    },
                    scales: {
                        y1: {
                            // min: -15,
                            // max: 15,
                            grid: {
                                color: function(context) {
                                    if (context.tick.value == 0) {
                                        return "#000000";
                                    } else {
                                        return "#dddddd";
                                    }
                                },
                                lineWidth: function(context) {
                                    if (context.tick.value == 0) {
                                        return 2;
                                    } else {
                                        return 1;
                                    }
                                }
                            },
                        },
                        x1: {
                            grid: {
                                display: false
                            },
                        }
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return tooltipItem.yLabel;
                            }
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });
        });

}


window.onload = function () {
    update();
    setTimeout(function () {
        document.getElementById('loading-screen').style.display = 'none';
    }, 1000);

    fetch("/" + tournament_id + "/check-fencer-login?fencer_id=" + fencer_id, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((data) => {
        if (data["success"] === true) {
            document.getElementById("Button-ChangeInformationForm").style.display = "flex";
            logged_in_fencer = true;
            console.log("Logged in as fencer");
        } else {
            logged_in_fencer = false;
        }
    });

    fetch("/" + tournament_id + "/check-login", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((data) => {
        if (data["success"] === true) {
            document.getElementById("Button-ChangeInformationForm").style.display = "flex";
            logged_in_master = true;
            console.log("Logged in as master");
        } else {
            logged_in_master = false;
        }
    });
}

// Update every 10 seconds
setInterval(function () { update() }, 10000);



function standings(content) {
    let group;
    if (content === "all") {
        group = "all";
    } else if (content === "group") {
        group = document.getElementById("Group_Number").innerHTML;
    }

    window.open("/" + tournament_id + "/standings?group=" + group, "_blank");

}

document.querySelector("#Next-Piste-Block").addEventListener("click", (event) => {
    let pisteHelper = document.querySelector(".piste_helper");
    pisteHelper.classList.toggle("hide");
});


function viewTableau() {
    let group = document.getElementById("Group_Number").innerHTML;
    window.open("/" + tournament_id + "/tableau?group=" + group, "_blank");
}

function viewBrackets() {
    window.open("/" + tournament_id + "/brackets?fencer_id=" + fencer_id, "_blank");
}

function startMatch() {
    fetch("/api/matches/set-active?tournament_id=" + tournament_id + "&match_id=" + document.getElementById("Next-Match-Section").dataset.id, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: {"override_flag": "false"},
    })
        .then((response) => response.json())
        .then((data) => {
            if (Object.keys(data).includes("error")) {
                console.log(data["error"]);
                alert_string = "Error: " + data["error"]["code"];
                if (data["error"]["message"]) {
                    alert_string += "\n\n" + data["error"]["message"];
                }
                alert_string += "\n Do you want to view the logs?";
                if (data["error"]["exception"]) {
                    alert_string += "\n\n" + data["error"]["exception"];
                }
                var result = window.confirm(alert_string);
                if (result == true) {
                    window.open("/logs", "_blank");
                }
            } else {
                update();
            }
        }
    );
}

function inputScore() {

}

function pushScore() {

}

function report_issue() {
    alert("Please report the issue directly to the tournament director.");
}

function approve_tableau() {
    let url = window.location.href;
    let tournament = url.split("/")[3];
    let group = document.getElementById("Group_Number").innerHTML;
    let round = 1;
    let fencer_id = url.split("/")[5];
    // get current timestamp
    let timestamp = new Date()
    timestamp = timestamp.toISOString();
    let data = {
        "timestamp": timestamp,
        "group": group,
        "round": round,
        "tournament": tournament,
        "fencer_id": fencer_id
    }

    fetch("/api/fencer/approve-tableau?tournament_id=" + tournament_id + "&fencer_id=" + fencer_id, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then((response) => {
        return response.json();
    }
    ).then((data) => {
        if (data["success"] === true) {
            alert("Tableau approved!");
            document.getElementById("approval-needed").style.display = "none";
        } else {
            alert("Error! Tableau already approved or something went wrong!");
        }
    });
}

function changeInformationForm(event) {
    event.preventDefault();
    
    fetch("/api/fencer/change-attribute?tournament_id=" + tournament_id + "&fencer_id=" + fencer_id, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "attribute": document.getElementById("Change-Attribute").value,
            "value": document.getElementById("Change-Value").value,
        })
    }).then((response) => {
        return response.json();
    }
    ).then((data) => {
        if (Object.keys(data).includes("error")) {
            console.log(data["error"]);
            alert_string = "Error: " + data["error"]["code"];
            if (data["error"]["message"]) {
                alert_string += "\n\n" + data["error"]["message"];
            }
            alert_string += "\n Do you want to view the logs?";
            if (data["error"]["exception"]) {
                alert_string += "\n\n" + data["error"]["exception"];
            }
            var result = window.confirm(alert_string);
            if (result == true) {
                window.open("/logs", "_blank");
            }
        } else {
            alert("Attribute changed!\n\nAttribute: " + document.getElementById("Change-Attribute").value + "\nValue: " + document.getElementById("Change-Value").value);
            window.location.reload();
        }
    });
}

function displayChangeInformationForm() {
    let changeInformationWrapper = document.getElementById("Change-Information-Wrapper");
    if (changeInformationWrapper.style.display === "block") {
        changeInformationWrapper.style.display = "none";
    } else {
        changeInformationWrapper.style.display = "block";
    }
}

