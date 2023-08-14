<script lang="ts">
	import { page } from '$app/stores';
	import Navbar from '$lib/components/Navbar.svelte';
	import { onMount } from 'svelte';
	import { pageTitle, standingsData, tournamentData, userData } from '$lib/stores';
    const prefix = 'http://127.0.0.1:8080';

	onMount(async () => {
		setInterval(async () => {
			const fetchedUserData = await fetch(
				`${prefix}/api/fencer/update?tournament_id=${$page.params.tournament}&fencer_id=${$page.params.fencer}`
			).then((r) => r.json());
			userData.set(fetchedUserData);
		}, 1000);

        setInterval(async () => {
            const fetchedStandingsData = await fetch(
                `${prefix}/api/standings/update?tournament_id=${$page.params.tournament}`
            ).then((r) => r.json());
            standingsData.set(fetchedStandingsData);
        }, 30000);

        setInterval(async () => {
            const fetchedTournamentData = await fetch(
                `${prefix}/api/dashboard/update?tournament_id=${$page.params.tournament}`
            ).then((r) => r.json());
            tournamentData.set(fetchedTournamentData);
        }, 30000);
	});
</script>

<div class="flex flex-col items-stretch">
	<Navbar>
		<slot />
	</Navbar>
</div>
