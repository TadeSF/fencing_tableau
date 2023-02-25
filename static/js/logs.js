function get_logs(){
    const tournament_canvas = document.getElementById("Tournament");

    let password = document.getElementById("pw").value;

    tournament_canvas.innerHTML = ""

    fetch("/logs/get",
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "password": password
        })
    })
    .then(response => response.json())
    .then(data => {
        let tournament_logs = data.tournament_logs;

        for (let i = 0; i < tournament_logs.length; i++) {
            let log = tournament_logs[i];

            let log_element = document.createElement("div");
            log_element.classList.add("Log-Line");

            let datetime = document.createElement("div")
            datetime.innerHTML = tournament_logs[i]["datetime"]
            datetime.classList.add("datetime")

            let log_module = document.createElement("div")
            log_module.innerHTML = tournament_logs[i]["module"]
            log_module.classList.add("module")

            let log_level = document.createElement("div")
            log_level.innerHTML = tournament_logs[i]["level"]
            log_level.classList.add("level")
            log_level.classList.add(tournament_logs[i]["level"])

            let log_message = document.createElement("div")
            log_message.innerHTML = tournament_logs[i]["message"]
            log_message.classList.add("message")
            
            log_element.appendChild(datetime);
            log_element.appendChild(log_module);
            log_element.appendChild(log_level);
            log_element.appendChild(log_message);

            if (tournament_logs[i]["traceback"] != null) {
                let traceback_array = []
                
                for (let j = 0; j < tournament_logs[i]["traceback"].length; j++) {
                    traceback_array.push(tournament_logs[i]["traceback"][j])
                }
                
                let traceback = document.createElement("div")
                traceback.innerHTML = traceback_array.join("<br>")
                traceback.classList.add("traceback")
                traceback.style.display = "none"
                
                let traceback_button = document.createElement("button")
                let traceback_icon = document.createElement("i")
                traceback_icon.classList.add("fa-solid", "fa-chevron-down")
                traceback_button.appendChild(traceback_icon)
                traceback_button.classList.add("traceback-button")
                traceback_button.addEventListener("click", function() {
                    traceback.style.display = (traceback.style.display == "none") ? "block" : "none";
                    traceback_icon.classList.toggle("fa-chevron-down");
                    traceback_icon.classList.toggle("fa-chevron-up")
                })
                log_element.appendChild(traceback);
                log_element.appendChild(traceback_button);
            }

            tournament_canvas.appendChild(log_element);
        }
    });
}