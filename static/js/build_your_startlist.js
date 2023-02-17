let suggestions = [
    "vnm",
    "tur",
    "mys",
    "sen",
    "aze",
    "lka",
    "gnq",
    "gbr",
    "nga",
    "uga",
    "ecu",
    "gum",
    "sgp",
    "deu",
    "cog",
    "fsm",
    "mac",
    "vat",
    "abw",
    "jpn",
    "mus",
    "tls",
    "can",
    "nru",
    "pol",
    "plw",
    "pcn",
    "brn",
    "eth",
    "guy",
    "sgs",
    "jey",
    "cze",
    "hkg",
    "spm",
    "mwi",
    "cym",
    "mlt",
    "hrv",
    "ukr",
    "bhs",
    "ita",
    "rus",
    "bhr",
    "fro",
    "mar",
    "zwe",
    "kr",
    "fji",
    "myt",
    "ssd",
    "srb",
    "mtq",
    "mco",
    "ton",
    "dji",
    "gtm",
    "npl",
    "gnb",
    "usa",
    "pyf",
    "sdn",
    "moz",
    "mmr",
    "vut",
    "maf",
    "tuv",
    "and",
    "syc",
    "arm",
    "slb",
    "eri",
    "wlf",
    "nld",
    "btn",
    "ken",
    "ac",
    "msr",
    "stp",
    "ago",
    "dza",
    "mrt",
    "vgb",
    "tw",
    "smr",
    "som",
    "slv",
    "lby",
    "lbn",
    "gib",
    "ltu",
    "bwa",
    "irq",
    "mhl",
    "ta",
    "hmd",
    "svn",
    "aia",
    "cpv",
    "flk",
    "cri",
    "syr",
    "mex",
    "mkd",
    "egy",
    "ncl",
    "idn",
    "grl",
    "sau",
    "sle",
    "ven",
    "svk",
    "md",
    "swz",
    "sur",
    "nzl",
    "prt",
    "isr",
    "khm",
    "esh",
    "ggy",
    "bvt",
    "phl",
    "gha",
    "blm",
    "blz",
    "asm",
    "civ",
    "che",
    "qat",
    "un",
    "jor",
    "bol",
    "umi",
    "kir",
    "lva",
    "irl",
    "lbr",
    "grc",
    "pry",
    "lca",
    "are",
    "bq",
    "sxm",
    "mdg",
    "arg",
    "jam",
    "dma",
    "kgz",
    "irn",
    "esp",
    "per",
    "uzb",
    "lux",
    "xk",
    "vir",
    "afg",
    "tjk",
    "chn",
    "xx",
    "grd",
    "bmu",
    "pri",
    "reu",
    "gin",
    "est",
    "nam",
    "lao",
    "hun",
    "dom",
    "tz",
    "hnd",
    "cd",
    "mdv",
    "dnk",
    "tkl",
    "tgo",
    "blr",
    "isl",
    "geo",
    "nor",
    "prk",
    "hti",
    "chl",
    "tkm",
    "tha",
    "cp",
    "swe",
    "ic",
    "ala",
    "vct",
    "aut",
    "zaf",
    "atg",
    "fra",
    "tca",
    "kaz",
    "bel",
    "bgd",
    "glp",
    "niu",
    "lso",
    "nic",
    "gmb",
    "yem",
    "bfa",
    "bdi",
    "bgr",
    "mne",
    "atf",
    "ea",
    "cuw",
    "alb",
    "cub",
    "cxr",
    "dg",
    "col",
    "mng",
    "mnp",
    "wsm",
    "guf",
    "kna",
    "rwa",
    "pan",
    "kwt",
    "imn",
    "gab",
    "ben",
    "caf",
    "cmr",
    "com",
    "eu",
    "tun",
    "ata",
    "rou",
    "nfk",
    "ury",
    "pak",
    "iot",
    "brb",
    "bih",
    "zmb",
    "cck",
    "aus",
    "tto",
    "fin",
    "cyp",
    "sjm",
    "sh",
    "ps",
    "mli",
    "tcd",
    "lie",
    "png",
    "ind",
    "ner",
    "bra",
    "cok",
    "omn",
    "uno",
    "xxx",
];
suggestions.sort();

const startlist_id = document.getElementById("htmlbody").dataset.startlist_id;

function get_startlist() {
    console.log("startlist_id: " + startlist_id);
    fetch("/build-your-startlist/get-startlist?id=" + startlist_id, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then((response) => response.json())
    .then((data) => {
        const table_body = document.getElementsByClassName("body")[0];

        if (data["success"] == true) {
            let startlist = data["startlist"];
            for (let i = 0; i < startlist.length; i++) {
                let item_index = document.createElement("div");
                item_index.classList.add("body", "cell", "index");
                item_index.innerHTML = i + 1;

                let item_name = document.createElement("div");
                item_name.classList.add("body", "cell", "name");
                item_name.innerHTML = startlist[i][0];

                let item_club = document.createElement("div");
                item_club.classList.add("body", "cell", "club");
                item_club.innerHTML = startlist[i][1];

                let item_nationality = document.createElement("div");
                item_nationality.classList.add("body", "cell", "nationality");
                let flag = document.createElement("img");
                flag.classList.add("flag");
                flag.src = "/static/flags/" + startlist[i][2] + ".svg";
                item_nationality.appendChild(flag);

                let item_gender = document.createElement("div");
                item_gender.classList.add("body", "cell", "gender");
                item_gender.innerHTML = startlist[i][3];

                let item_handedness = document.createElement("div");
                item_handedness.classList.add("body", "cell", "handedness");
                item_handedness.innerHTML = startlist[i][4];

                let item_age = document.createElement("div");
                item_age.classList.add("body", "cell", "age");
                item_age.innerHTML = startlist[i][5];

                let item_delete = document.createElement("div");
                item_delete.classList.add("body", "cell", "delete");
                let delete_button = document.createElement("i");
                delete_button.classList.add("fa-solid", "fa-trash");
                delete_button.onclick = function() {
                    delete_fencer(i + 1);
                };
                item_delete.appendChild(delete_button);

                table_body.appendChild(item_index);
                table_body.appendChild(item_name);
                table_body.appendChild(item_club);
                table_body.appendChild(item_nationality);
                table_body.appendChild(item_gender);
                table_body.appendChild(item_handedness);
                table_body.appendChild(item_age);
                table_body.appendChild(item_delete);
            }

        } else {
            console.log("error");
        }
    });
}

function addFencer() {
    if (document.getElementById("name").value == "") {
        alert("Please enter a name");
        return;
    } else if (document.getElementById("club").value == "") {
        alert("Please enter a club");
        return;
    } else if (document.getElementById("nationality-input").value == "") {
        alert("Please enter a Country-Code");
        return;
    // else if countr-input is not in the list of country codes
    } else if (suggestions.includes(document.getElementById("nationality-input").value.toLowerCase()) == false) {
        alert("Please enter a valid Country-Code");
        return;
    }

    FormData = {
        "startlist_id": startlist_id,
        "name": document.getElementById("name").value,
        "club": document.getElementById("club").value,
        "nationality": document.getElementById("nationality-input").value,
        "gender": document.getElementById("gender").value,
        "handedness": document.getElementById("handedness").value,
        "age": document.getElementById("age").value,
    };

    fetch("/build-your-startlist/add-fencer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(FormData),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data["success"] == true) {
            window.location.reload();
        } else {
            console.log("error");
        }
    });
}

function delete_fencer(fencer_id) {
    FormData = {
        "startlist_id": startlist_id,
        "row_number": fencer_id,
    };
    fetch("/build-your-startlist/delete-fencer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(FormData),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data["success"] == true) {
            window.location.reload();
        } else {
            console.log("error");
        }
    });
}

function saveStartlist() {
    window.open("/build-your-startlist/save-startlist?id=" + startlist_id, "_blank");
}

window.onload = function() {
    get_startlist();
};


function showSuggestions() {
    const input = document.getElementById("nationality-input");
    const dropdown = document.getElementById("nationality-dropdown");
    const filter = input.value.toUpperCase();

    dropdown.innerHTML = "";
    let suggestions_count = 0;
    suggestions.forEach((option) => {
        if (option.toUpperCase().indexOf(filter) > -1) {
            const link = document.createElement("a");
            link.textContent = option.toUpperCase();
            link.setAttribute("href", "#");
            link.addEventListener("click", () => {
                input.value = option.toUpperCase();
                dropdown.style.display = "none";
            });
            dropdown.appendChild(link);
            suggestions_count += 1;
        }
    });

    if (input.value.length === 3) {
        dropdown.style.display = "none";
        input.style.color = "white";
        if (suggestions.includes(input.value.toLowerCase()) == true) {
            input.style.backgroundColor = "green";
        } else {
            input.style.backgroundColor = "red";
        }
    } else if (dropdown.innerHTML === "") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
}