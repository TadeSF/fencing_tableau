// When button "Start Tournament" is clicked, this function is called
function start_tournament() {
  fetch('http://127.0.0.1:5000/json-example', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    key: 'Hello World!'
    })
  });
}

window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};