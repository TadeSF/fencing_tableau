import type { PageLoad } from './$types';
import { userData, standingsData, tournamentData } from '$lib/stores';

export const load = (async ({ params, fetch }) => {
	const prefix = "http://127.0.0.1:8080";

	const fetchedUserData = await fetch(
		`${prefix}/api/fencer/update?tournament_id=${params.tournament}&fencer_id=${params.fencer}`
	).then((r) => r.json());
	userData.set(fetchedUserData);

	const fetchedStandingsData = await fetch(
		`${prefix}/api/standings/update?tournament_id=${params.tournament}`
	).then((r) => r.json());
	standingsData.set(fetchedStandingsData);

	const fetchedTournamentData = await fetch(
		`${prefix}/api/dashboard/update?tournament_id=${params.tournament}`
	).then((r) => r.json());
	tournamentData.set(fetchedTournamentData);

	return {
		props: {
			tournament: params.tournament,
			fencer: params.fencer
		}
	};
}) satisfies PageLoad;
