const id = document.getElementById("body").dataset.tournament_id;
const url = "https://fencewithfriends.online/fencer-login?tournament=" + id;

window.onload = function() {
    let qr_code = new QRCode(document.getElementById("qr_code"), {
        width: 200,
        height: 200,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
    qr_code.makeCode(url);
    
    let link = document.getElementById("link");
    link.value = url;
    link.select();
}

function copy_link() {
    let link = document.getElementById("link");
    link.select();
    document.execCommand("copy");
    alert("Copied link to clipboard!");
}