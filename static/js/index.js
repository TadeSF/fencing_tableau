// When button "Start Tournament" is clicked, this function is called
function new_tournament() {
  // Show the new_tournament_form div
  window.open("/get-started", "_self")
}

// When button "Manage existing Tournament" is clicked, this function is called
function login_manager() {
  // Show the new_tournament_form div
  window.open("/tournaments", "_self")
}


// When button "Log in as Participant" is clicked, this function is called
function login_fencer() {
  // Show the new_tournament_form div
  window.open("/fencer-login", "_self")
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

function openUserguide() {
  window.open('/docs/Userguide', '_blank')
}


window.onerror = function(error, url, line) {
  alert("An error occurred: " + error + "\nOn line: " + line + "\nIn file: " + url);
};


window.onload = function() {
  const cookieBanner = document.getElementById("cookieBanner");
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

