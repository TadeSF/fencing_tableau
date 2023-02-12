window.onload = function() {
    url = window.location.href;
    // if url has a "?tournament=" parameter, pre-input the tournament id
    if (url.indexOf("?tournament=") != -1) {
        var tournament_id = url.split("?tournament=")[1];
        console.log(tournament_id);
        document.getElementById("fencer_tournament_id").value = tournament_id;
    }
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
        error_div.innerHTML = 'Fencer found:<br>' + data.description + '<br>Redirecting...<br><br>If you are not redirected, click <a href="' + data.tournament_id + '/fencer/' + data.fencer_id + '">here</a>';
        error_div.style.background = "green";
        // wait for 2 seconds
        setTimeout(function(){
            // redirect to the fencer page according to the fencer_id
            url = data.tournament_id + "/fencer/" + data.fencer_id;
            window.open(url, "_self")
        }, 2000);
  
      }
    })
    .catch(error => {
      console.log(error);
      document.getElementById("fencer-error-message").innerHTML = error;
    });
  }