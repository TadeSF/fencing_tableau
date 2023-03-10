const tournament_id = document.body.dataset.tournament_id;
const highlighted_fencer_id = document.body.dataset.highlighted_fencer_id;

function update(data) {
    const data_keys = Object.keys(data).reverse();
    for (const stage of data_keys) {
        if (stage == "title") {
            document.getElementById("bracket_title").innerHTML = data["title"];
        } else {
            // create the stage column
            const stage_column = document.createElement("div");
            stage_column.classList.add("tournament-bracket__round");
            stage_column.id = stage;

            const stage_title = document.createElement("h3");
            stage_title.classList.add("tournament-bracket__round-title");
            console.log(data[stage][data[stage].length - 1]);
            console.log(data[stage]);
            stage_title.innerHTML = data[stage][data[stage].length - 1];
            stage_column.appendChild(stage_title);

            const stage_list = document.createElement("ul");
            stage_list.classList.add("tournament-bracket__list");
            stage_column.appendChild(stage_list);

            for (const node in data[stage]) {
                // continue if node is not an object (match) but a string
                if (typeof data[stage][node] !== "object") {
                    continue;
                }

                const node_data = data[stage][node];

                // create node
                const node_element = document.createElement("li");
                node_element.classList.add("tournament-bracket__item");
                stage_list.appendChild(node_element);

                // create node content
                const node_content = document.createElement("div");
                node_content.classList.add("tournament-bracket__match");
                if (node_data["red_id"] == highlighted_fencer_id || node_data["green_id"] == highlighted_fencer_id) {
                    node_content.classList.add("highlighted");
                }
                node_content.tabIndex = 0;
                node_element.appendChild(node_content);

                const node_table = document.createElement("table");
                node_table.classList.add("tournament-bracket__table");
                node_content.appendChild(node_table);

                const node_table_body = document.createElement("tbody");
                node_table_body.classList.add("tournament-bracket__content");
                node_table.appendChild(node_table_body);

                // Red Fencer
                const node_table_row = document.createElement("tr");
                node_table_row.classList.add("tournament-bracket__team");
                if (node_data["red_score"] > node_data["green_score"]) {
                    node_table_row.classList.add("tournament-bracket__team--winner");
                }
                node_table_body.appendChild(node_table_row);

                const node_red_cell = document.createElement("td");
                node_red_cell.classList.add("tournament-bracket__country");
                node_table_row.appendChild(node_red_cell);

                const node_red_name = document.createElement("span");
                node_red_name.classList.add("tournament-bracket__code");
                node_red_name.innerHTML = node_data["red"];
                node_red_cell.appendChild(node_red_name);

                const node_red_flag = document.createElement("span");
                node_red_flag.classList.add("tournament-bracket__flag");
                const node_red_img = document.createElement("img");
                node_red_img.src = "/static/flags/" + node_data["red_nationality"].toLowerCase() + ".svg";
                node_red_flag.appendChild(node_red_img);
                node_red_cell.appendChild(node_red_flag);

                const node_red_score = document.createElement("td");
                node_red_score.classList.add("tournament-bracket__score");
                const node_red_score_span = document.createElement("span");
                node_red_score_span.innerHTML = node_data["red_score"];
                node_red_score_span.classList.add("tournament-bracket__number");
                node_red_score.appendChild(node_red_score_span);
                node_table_row.appendChild(node_red_score);

                // Green Fencer
                const node_table_row2 = document.createElement("tr");
                node_table_row2.classList.add("tournament-bracket__team");
                if (node_data["green_score"] > node_data["red_score"]) {
                    node_table_row2.classList.add("tournament-bracket__team--winner");
                }
                node_table_body.appendChild(node_table_row2);

                const node_green_cell = document.createElement("td");
                node_green_cell.classList.add("tournament-bracket__country");
                node_table_row2.appendChild(node_green_cell);

                const node_green_name = document.createElement("span");
                node_green_name.classList.add("tournament-bracket__code");
                node_green_name.innerHTML = node_data["green"];
                node_green_cell.appendChild(node_green_name);

                const node_green_flag = document.createElement("span");
                node_green_flag.classList.add("tournament-bracket__flag");
                const node_green_img = document.createElement("img");
                node_green_img.src = "/static/flags/" + node_data["green_nationality"].toLowerCase() + ".svg";
                node_green_flag.appendChild(node_green_img);
                node_green_cell.appendChild(node_green_flag);

                const node_green_score = document.createElement("td");
                node_green_score.classList.add("tournament-bracket__score");
                const node_green_score_span = document.createElement("span");
                node_green_score_span.innerHTML = node_data["green_score"];
                node_green_score_span.classList.add("tournament-bracket__number");
                node_green_score.appendChild(node_green_score_span);
                node_table_row2.appendChild(node_green_score);
            }

            document.getElementById("bracket").appendChild(stage_column);
        }
    }   

}

function get_data() {
    fetch('/api/brackets/update?tournament_id=' + tournament_id, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
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
                update(data);
            }
        });
}

get_data();