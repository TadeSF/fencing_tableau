function submitStartForm(event) {
    event.preventDefault();

    document.getElementById('submit_icon').classList.remove('fa-paper-plane');
    document.getElementById('submit_icon').classList.add('fa-spinner');
    document.getElementById('submit_icon').classList.add('fa-spin');

    document.getElementById('submit').disabled = true;

    if (document.getElementById('hidden_recaptcha').checked == true) {
        // raise error
        document.getElementById('submit_icon').classList.remove('fa-spinner');
        document.getElementById('submit_icon').classList.remove('fa-spin');
        document.getElementById('submit_icon').classList.add('fa-paper-plane');
        document.getElementById('submit').disabled = false;
        alert("You are a bot!")
    } else {

        const formData = new FormData();
        formData.append('name', document.getElementById('name').value);
        formData.append('location', document.getElementById('location').value);
        formData.append('fencers', document.getElementById('fencers').files[0]);
        formData.append('pistes', document.getElementById('pistes').value);
        formData.append('piste_assignment_mode', document.getElementById('piste_assignment').value);
        formData.append('number_of_preliminary_rounds', document.getElementById('number_of_preliminary_rounds').value);
        formData.append('number_of_preliminary_groups', document.getElementById('number_of_preliminary_groups').value);
        formData.append('first_elimination_round', document.getElementById('first_elimination_round').value);
        formData.append('elimination_mode', document.getElementById('elimination_mode').value);
        formData.append('simulation_active', document.getElementById('simulation_active').value);
        formData.append('master_password', document.getElementById('master_password').value);
        formData.append('master_email', document.getElementById('master_email').value);

        fetch('/get-started', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success == true) {
                window.open(data.tournament_id + "/dashboard", "_self")
            } else {
                console.log(data.error)
                document.getElementById('submit_icon').classList.remove('fa-spinner');
                document.getElementById('submit_icon').classList.remove('fa-spin');
                document.getElementById('submit_icon').classList.add('fa-paper-plane');
                document.getElementById('submit').disabled = false;
                alert(data.error + "\n" + data.message)
            }
        })
        .catch(error => {
            document.getElementById('submit_icon').classList.remove('fa-spinner');
            document.getElementById('submit_icon').classList.remove('fa-spin');
            document.getElementById('submit_icon').classList.add('fa-paper-plane');
            document.getElementById('submit').disabled = false;
            console.error(error);
            alert(data.error)
        });
    }
}

function checkPasswordMatch() {
    const password = document.getElementById("master_password");
    const confirmPassword = document.getElementById("master_password_confirm");

    if (password.value != confirmPassword.value) {
        confirmPassword.setCustomValidity("Passwords do not match.");
    } else {
        confirmPassword.setCustomValidity('');
    }
}