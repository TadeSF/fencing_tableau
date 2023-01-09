// When button "Start Tournament" is clicked, this function is called
function new_tournament() {
  // Show the new_tournament_form div
  document.getElementById("new_tournament_form").style.display = "block";
}

document.addEventListener('click', (event) => {
  if (!document.getElementById("start_form").contains(event.target) && !document.getElementById("start_tournament").contains(event.target)) {
    document.getElementById("new_tournament_form").style.display = 'none';
  }
});

// When button "Manage existing Tournament" is clicked, this function is called
function login_manager() {
  // Show the new_tournament_form div
  document.getElementById("login_manager_form").style.display = "block";
}

document.addEventListener('click', (event) => {
  if (!document.getElementById("master_login_form").contains(event.target) && !document.getElementById("button_manage").contains(event.target)) {
    document.getElementById("login_manager_form").style.display = 'none';
  }
});


// When button "Log in as Participant" is clicked, this function is called
function login_fencer() {
  // Show the new_tournament_form div
  document.getElementById("login_fencer_form").style.display = "block";
}

document.addEventListener('click', (event) => {
  if (!document.getElementById("fencer_login_form").contains(event.target) && !document.getElementById("button_participate").contains(event.target)) {
    document.getElementById("login_fencer_form").style.display = 'none';
  }
});


window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};
