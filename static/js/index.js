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

function submitFencerForm(event) {
  event.preventDefault();

  console.log("fencer_tournament_id: " + document.getElementById('fencer_tournament_id').value);
  console.log("fencer_search: " + document.getElementById('fencer_search').value);
  fetch('/login-fencer', { 
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      tournament_id: document.getElementById('fencer_tournament_id').value,
      search: document.getElementById('fencer_search').value,
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log(data.error)
    let error_div = document.getElementById("fencer-error-message")
    if(data.error) {
      error_div.style.display = "block";
      error_div.innerHTML = data.error;
      error_div.style.background = "red";
    } else {
      error_div.style.display = "block";
      error_div.innerHTML = 'Fencer found:<br>' + data.description + '<br>Redirecting...';
      error_div.style.background = "green";
      // wait for 2 seconds
      setTimeout(function(){
        // redirect to the fencer page according to the fencer_id
        url = data.tournament_id + "/fencer/" + data.fencer_id;
        error_div.style.display = "none";
        window.open(url, null)
      }, 2000);

    }
  })
  .catch(error => {
    console.log(error);
    document.getElementById("fencer-error-message").innerHTML = error;
  });
}



// When button "Log in as Participant" is clicked, this function is called
function login_referee() {
  // Show the new_tournament_form div
  document.getElementById("login_referee_form").style.display = "block";
}

document.addEventListener('click', (event) => {
  if (!document.getElementById("fencer_login_form").contains(event.target) && !document.getElementById("button_participate").contains(event.target)) {
    document.getElementById("login_fencer_form").style.display = 'none';
  }
});


window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};
