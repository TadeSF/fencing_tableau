
function update_time(string) {
  document.getElementById("time").innerHTML = string;
}

eel.expose(update_time);