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
  window.open("/tournaments", "_self")
}


// When button "Log in as Participant" is clicked, this function is called
function login_fencer() {
  // Show the new_tournament_form div
  window.open("/m", "_self")
}

function submitStartForm(event) {
  event.preventDefault();

  const formData = new FormData();
  formData.append('name', document.getElementById('name').value);
  formData.append('location', document.getElementById('location').value);
  formData.append('fencers', document.getElementById('fencers').files[0]);
  formData.append('pistes', document.getElementById('pistes').value);
  formData.append('number_of_preliminary_rounds', document.getElementById('number_of_preliminary_rounds').value);
  formData.append('number_of_preliminary_groups', document.getElementById('number_of_preliminary_groups').value);
  formData.append('first_elimination_round', document.getElementById('first_elimination_round').value);
  formData.append('elimination_mode', document.getElementById('elimination_mode').value);
  formData.append('simulation_active', document.getElementById('simulation_active').checked);
  formData.append('master_password', document.getElementById('master_password').value);


  fetch('/', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.success == true) {
        window.open(data.tournament_id + "/dashboard", "_self")
      } else {
        console.log(data.error)
        alert(data.error + "\n" + data.message)
      }
    })
    .catch(error => {
      console.error(error);
    });
}


function login_referee() {
  // Show the new_tournament_form div
  document.getElementById("login_referee_form").style.display = "block";
}

function openGithub() {
  window.open('https://github.com/TadeSF/fencing_tableau', '_blank')
}

function openDocumentation() {
  window.open('/docs', '_blank')
}


window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};


window.onload = function() {
  const cookieBanner = document.getElementById("cookieBanner");
  console.log(document.cookie)
  if (document.cookie.indexOf("cookieConsent=true") === -1) {
    cookieBanner.style.display = "block";
  } else {
    cookieBanner.style.display = "none";
  }
};

function acceptCookies() {
  cookieBanner.style.display = "none";
  document.cookie = "cookieConsent=true; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/";
}