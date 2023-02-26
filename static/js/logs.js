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

        for (const element of tournament_logs) {

            let log_element = document.createElement("div");
            log_element.classList.add("Log-Line");

            let datetime = document.createElement("div")
            datetime.innerHTML = element["datetime"]
            datetime.classList.add("datetime")

            let log_module = document.createElement("div")
            log_module.innerHTML = element["module"]
            log_module.classList.add("module")

            let log_level = document.createElement("div")
            log_level.innerHTML = element["level"]
            log_level.classList.add("level")
            log_level.classList.add(element["level"])

            let log_message = document.createElement("div")
            log_message.innerHTML = element["message"]
            log_message.classList.add("message")
            
            log_element.appendChild(datetime);
            log_element.appendChild(log_module);
            log_element.appendChild(log_level);
            log_element.appendChild(log_message);

            if (element["traceback"] != null) {
                let traceback_array = []
                
                for (let j = 0; j < element["traceback"].length; j++) {
                    traceback_array.push(element["traceback"][j])
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