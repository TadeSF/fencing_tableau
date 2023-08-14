<script lang="ts">
	import type { LayoutData } from './$types';
    import { standingsData } from '$lib/stores';
    import { page } from '$app/stores';

    const prefix = 'http://127.0.0.1:8080';

	setInterval(async () => {
		const fetchedStandingsData = await fetch(
			`${prefix}/api/standings/update?tournament_id=${$page.params.tournament}`
		).then((r) => r.json());
		standingsData.set(fetchedStandingsData);
	}, 1000);
</script>

<slot />
