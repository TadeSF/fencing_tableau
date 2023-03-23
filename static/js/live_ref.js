const tournament_id = document.body.dataset.tournament_id;
const match_id = document.body.dataset.match_id;

let countdownTimer;
let setsRemaining = 3;
let timeLeft = 180;
let passivTimer = 60;
let isBreak = false;
const timerDisplay = document.getElementById("Timer-Display");
const passivTimerDisplay = document.getElementById("Passiv-Timer");
const setsDisplay = document.getElementById("Sets");
const startStopBtn = document.getElementById("Start-Stop-Button");
const button_icon = startStopBtn.children[0].children[0];
const buzzer_sound = new Audio("/static/sounds/buzzer.wav");

// hide send score button if no match id is given
if (match_id === "None") {
    document.getElementById("Send-Score").style.display = "none";
}

function update_score(element) {
    let score;
    let score_element;
    
    if (element.id === 'Plus-Red' || element.id === 'Minus-Red') {
        score_element = document.getElementById('Score-Red');
    } else {
        score_element = document.getElementById('Score-Green');
    };

    score = parseInt(score_element.innerHTML);
    
    if (element.classList.contains('Score-Button--Plus')) {
        score += 1;
    } else {
        score -= 1;
    };

    if (score < 0) {
        score = 0;
    } else if (score > 15) {
        score = 15;
    } else {
        passivTimer = 60;
        passivTimerDisplay.textContent = "01:00";
    };

    score_element.innerHTML = score.toString();
}


function startTimer() {
    countdownTimer = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(countdownTimer);
            if (isBreak) {
                setsRemaining--;

                setsDisplay.textContent = `${4 - setsRemaining} / 3`;
                console.log(setsRemaining);
                
                button_icon.classList.remove("fa-coffee");
                button_icon.classList.add("fa-play");
                // Play sound
                buzzer_sound.play();
                isBreak = false;
                timeLeft = 180;
                timerDisplay.textContent = "03:00";
            } else {
                isBreak = true;
                timeLeft = 60; // total time in seconds for each break (1 minute)
                passivTimerDisplay.textContent = "01:00";
                passivTimer = 60;
                if (setsRemaining > 1) {
                    timerDisplay.textContent = "00:00";
                    button_icon.classList.remove("fa-play");
                    button_icon.classList.remove("fa-pause");
                    button_icon.classList.add("fa-coffee");
                    startTimer();
                } else {
                    clearInterval(countdownTimer);
                    timerDisplay.textContent = "Finished"
                }
                buzzer_sound.play();
            }
        } else {
            if (passivTimer <= 0) {
                clearInterval(countdownTimer);
                passivTimer = 60;
                buzzer_sound.play();
                // wait until sound is finished
                setTimeout(() => {}, 1000);
                alert("Passiv time is over!");
                button_icon.classList.remove("fa-pause");
                button_icon.classList.add("fa-play");
            }

            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

            const passiv_minutes = Math.floor(passivTimer / 60);
            const passiv_seconds = passivTimer % 60;
            passivTimerDisplay.textContent = `${passiv_minutes.toString().padStart(2, "0")}:${passiv_seconds.toString().padStart(2, "0")}`;

            timeLeft--;
            if (!isBreak) {
                passivTimer--;
            }
        }
    }, 1000);
}


function stopTimer() {
    clearInterval(countdownTimer);
}

startStopBtn.addEventListener("click", () => {
    if (isBreak) {
        return;
    }
    if (button_icon.classList.contains("fa-play")) {
        button_icon.classList.remove("fa-play");
        button_icon.classList.add("fa-pause");
        startTimer();
    } else {
        button_icon.classList.remove("fa-pause");
        button_icon.classList.add("fa-play");
        stopTimer();
    }
});

function changeTimer(interval) {
    // interval is in seconds
    timeLeft += interval;
    if (timeLeft < 1) {
        timeLeft = 1;

    }
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerDisplay.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

function resetAll() {
    if (confirm("Are you sure you want to reset the timer and scores?")) {
        clearInterval(countdownTimer);
        setsRemaining = 3;
        timeLeft = 180;
        isBreak = false;
        timerDisplay.textContent = "03:00";
        button_icon.classList.remove("fa-pause");
        button_icon.classList.remove("fa-coffee");
        button_icon.classList.add("fa-play");
        document.getElementById("Score-Red").innerHTML = "0";
        document.getElementById("Score-Green").innerHTML = "0";
        setsDisplay.textContent = "1 / 3";
        passivTimerDisplay.textContent = "01:00";
        passivTimer = 60;
    } else {
            return;
    }
}

function pushScore() {
    if (confirm("Are you sure you want to push the score to the database?")) {
        let score_red = document.getElementById("Score-Red").innerHTML;
        let score_green = document.getElementById("Score-Green").innerHTML;

        let data = {
            'green_score': score_green,
            'red_score': score_red
        }

        fetch('/api/matches/push-score?tournament_id=' + tournament_id + '&match_id=' + match_id, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
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
                    alert("Score pushed successfully");
                }
            })
    }
}