function formatTable(tableau) {
    var table = document.getElementById("tableau");



    for (var i = 0; i < tableau.length; i++) {
        var row = document.createElement("tr");
        for (var j = 0; j < tableau[i].length; j++) {
            if (i == 0) {
                var cell = document.createElement("th");
            } else {
                var cell = document.createElement("td");
            }

            if (tableau[i][j].cell_type == "blank") {
                cell.innerHTML = "";
                cell.className = "blank";

            } else if (tableau[i][j].cell_type == "blank_header") {
                cell.innerHTML = "";
                cell.className = "corner";

            } else if (tableau[i][j].cell_type == "header") {
                if (i == 0) {
                    var span = document.createElement("span");
                    span.innerHTML = tableau[i][j].name;
                    span.className = "rotate";
                    cell.appendChild(span);
                } else {
                    cell.innerHTML = tableau[i][j].name;
                }
                cell.className = "header";
                cell.dataset.id = tableau[i][j].id;
                if (tableau[i][j].approved == true) {
                    cell.style.color = "green";
                }
                
                cell.onclick = function () {
                    url = window.location.href;
                    url = url.split("/");
                    tournament = url[url.length - 4];
                    fencer = this.dataset.id;
                    window.open("/" + tournament + "/fencer/" + fencer, "_blank")
                }

            } else {
                if (tableau[i][j].finished == false) {
                    cell.innerHTML = "";
                } else {
                    cell.innerHTML = tableau[i][j].content;
                    if (tableau[i][j].win == true) {
                        cell.className = "win";
                    } else {
                        cell.className = "lose";
                    }
                }
                cell.classList.add("result");
                cell.dataset.id = tableau[i][j].match_id;
                cell.onclick = function () {
                    console.log(this.dataset.id);
                }
            }
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
}


function update() {
    var url = window.location.href;
    fetch(url + "/update")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            formatTable(data);
        });
}

window.onload = function () {
    update()
}

function print_page() {
    // print the current window
    window.print();
}

function back() {
    //close the current window
    window.close();
}