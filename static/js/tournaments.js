function ManageTournament(tournament_id) {
    window.open("/" + tournament_id + "/dashboard", "_self")
}

function LoginAsFencer(tournament_id) {
    window.open("/fencer-login?tournament=" + tournament_id, "_self")
}