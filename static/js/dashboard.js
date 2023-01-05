function generate_matches() {
    fetch('/dashboard/matches/generate')
}

window.onerror = function(error, url, line) {
    alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
  };