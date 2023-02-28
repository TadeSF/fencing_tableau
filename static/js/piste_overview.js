const pistes = document.body.dataset.num_pistes;
const tournament_id = document.body.dataset.tournament_id;


window.onload = function () {

    // Change the template-columns to display the right ammount of pistes
    const piste_container = document.getElementById("piste_container");
    piste_container.style.gridTemplateColumns = `repeat(${pistes}, minmax(220px, 1fr)) 1px`;

    // Create Pistes
    for (let i = 0; i < pistes; i++) {
        let piste = document.createElement("div");
        piste.classList.add("Piste");
        piste.classList.add("Loading")
        piste.id = `piste_${i}`;
        
        let s1 = document.createElement("div");
        s1.classList.add("Section");
        s1.classList.add("S-1");
        
        let status_button = document.createElement("div");
        status_button.classList.add("Button");
        let icon = document.createElement("i");
        icon.classList.add("fa-solid");
        icon.classList.add("fa-circle");
        status_button.appendChild(icon);
        s1.appendChild(status_button);

        let fencer_1 = document.createElement("div");
        fencer_1.classList.add("Fencer-Banner");
        fencer_1.classList.add("Fencer-Red");
        s1.appendChild(fencer_1);

        let fencer_2 = document.createElement("div");
        fencer_2.classList.add("Fencer-Banner");
        fencer_2.classList.add("Fencer-Green");
        s1.appendChild(fencer_2);

        let button_grid = document.createElement("div");
        button_grid.classList.add("Button-Grid");
        let toggle_piste = document.createElement("div");
        toggle_piste.classList.add("Button");
        toggle_piste.classList.add("Toggle-Piste");
        let toggle_piste_icon = document.createElement("i");
        toggle_piste_icon.classList.add("fa-solid");
        toggle_piste_icon.classList.add("fa-toggle-on");
        toggle_piste.appendChild(toggle_piste_icon);
        button_grid.appendChild(toggle_piste);
        s1.appendChild(button_grid);

        let s2 = document.createElement("div");
        s2.classList.add("Section");
        s2.classList.add("S-2");

        let img = document.createElement("img");
        img.src = "/static/img/endzone.svg";
        s2.appendChild(img);

        let s3 = document.createElement("div");
        s3.classList.add("Section");
        s3.classList.add("S-3");
        s3.innerHTML = i + 1;

        let bar = document.createElement("div");
        bar.classList.add("Section");
        bar.classList.add("Bar");

        let bar2 = document.createElement("div");
        bar2.classList.add("Section");
        bar2.classList.add("Bar");

        piste.appendChild(s1);
        piste.appendChild(bar);
        piste.appendChild(s2);
        piste.appendChild(bar2);
        piste.appendChild(s3);

        piste_container.appendChild(piste);
    }

    // Create the last placeholder piste
    let piste = document.createElement("div");
    piste.classList.add("Last-Banner");
    piste_container.appendChild(piste);

    // Get the piste status every 5 seconds
    get_piste_status();
    setInterval(get_piste_status, 5000);
};

function get_piste_status() {
    fetch("/" + tournament_id + "/piste-overview/get-status")
        .then(response => response.json())
        .then(data => {
            if (data["success"] === false) {
                alert("Error while getting piste status: " + data["message"]);
                return;
            }

            data = data["message"];
            console.log(data);
            for (let i = 0; i < data.length; i++) {
                let piste = document.getElementById(`piste_${i}`);
                piste.className = "Piste";
                let button_icon = piste.getElementsByClassName("fa-solid")[0]
                button_icon.className = "fa-solid";
                let button = piste.getElementsByClassName("Button")[0];
                let toggle_button = piste.getElementsByClassName("Toggle-Piste")[0];
                toggle_button.onclick = function () {
                    fetch("/" + tournament_id + "/piste-overview/toggle-piste", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            "piste": i + 1
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data["success"] === false) {
                                alert("Error while toggling piste: " + data["message"]);
                            } else {
                                get_piste_status();
                            }
                        });
                }
                let toggle_icon = toggle_button.getElementsByClassName("fa-solid")[0];
                toggle_icon.className = "fa-solid fa-toggle-on";
                
                
                if (data[i]["status"] === "occupied") {
                    piste.classList.add("Ongoing");
                    button_icon.classList.add("fa-spinner");
                    button_icon.classList.add("fa-spin");
                    
                } else if (data[i]["status"] === "staged") {
                    piste.classList.add("Staged");
                    button_icon.classList.add("fa-play");
                    button_icon.classList.add("fa-beat");
                    button.onclick = function () {
                        button_icon.classList.remove("fa-play");
                        button_icon.classList.remove("fa-beat");
                        button_icon.classList.add("fa-spinner");
                        button_icon.classList.add("fa-spin");
                        console.log(data[i]["match_id"]);
                        fetch("/" + tournament_id + "/matches/set_active", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                "id": data[i]["match_id"]
                            })
                        })
                            .then(response => response.json())
                            .then(data => {
                                if (data["success"] === false) {
                                    alert("Error while setting match as active: " + data["message"]);
                                } else {
                                    get_piste_status();
                                }
                            });
                    };

                } else if (data[i]["status"] === "disabled") {
                    piste.classList.add("Disabled");
                    button_icon.classList.add("fa-ban");
                    toggle_icon.classList.remove("fa-toggle-on");
                    toggle_icon.classList.add("fa-toggle-off");
                    

                } else if (data[i]["status"] === "free") {
                    button_icon.classList.add("fa-user-xmark");

                } else {
                    alert("Unknown piste status for piste " + i + ": " + data[i]["status"])
                    piste.classList.add("Loading");
                }

                if (data[i]["status"] === "occupied" || data[i]["status"] === "staged") {
                    let fencer_1 = piste.getElementsByClassName("Fencer-Red")[0];
                    let fencer_2 = piste.getElementsByClassName("Fencer-Green")[0];

                    fencer_1.innerHTML = data[i]["red"];
                    fencer_2.innerHTML = data[i]["green"];
                }
            }
        });
}

function toggle_piste(piste_id) {
    fetch("/" + tournament_id + "/piste-overview/toggle-piste", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "id": piste_id
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data["success"] === false) {
                alert("Error while toggling piste: " + data["message"]);
            } else {
                get_piste_status();
            }
        });
}