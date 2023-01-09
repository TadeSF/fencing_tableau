function generate_matches() {
    url = window.location.href
    id = url.split("/")[3]
    console.log(id)
    fetch('matches/generate')
}

window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
  };