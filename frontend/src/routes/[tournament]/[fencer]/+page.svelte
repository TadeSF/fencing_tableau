<script lang="ts">
	import NextMatch from '$lib/components/NextMatch.svelte';
	import StatsTeaser from '$lib/components/StatsTeaser.svelte';
	import MenuCard from '$lib/components/MenuCard.svelte';

	import type { PageData } from './$types';
	import { page } from '$app/stores';

	import { pageTitle, userData, tournamentData } from '$lib/stores';

	export let data: PageData;

	$: pageTitle.set($userData.name);

	const activeMatchColor = () => {
		return 'warning';
	};
</script>

<div class="hidden bg-primary" />
<div class="hidden bg-accent" />
<div class="w-full flex justify-center align-center">
	<div class="m-4 w-full flex flex-row gap-12 flex-wrap justify-center items-center">
		<div class="flex w-full flex-col justify-start items-start">
			<h2 class="text-xl font-bold">Welcome to {$tournamentData.name}!</h2>
			{#if $tournamentData.location}
			<h3 class="text-lg">Location: {$tournamentData.location}</h3>
			{/if}
		</div>
		<NextMatch showDetailsButton={true} />
		<StatsTeaser />
		<div class="w-full flex flex-col md:flex-row flex-wrap gap-8 justify-center align-center">
			<MenuCard
				headline="Matches"
				text="View all upcoming matches"
				buttonLink={`${$page.url.pathname}/matches`}
				transitionDelay={400}
			/>
			<MenuCard
				headline="Standings"
				text="View the Current Standings of the Tournament and your Group"
				buttonLink={`${$page.url.pathname}/standings`}
				transitionDelay={500}
			/>
			<MenuCard
				headline="Statistics"
				text="See all stats and analytics of your performance"
				buttonLink={`${$page.url.pathname}/stats`}
				buttonLabel={'View Stats'}
				transitionDelay={600}
			/>
		</div>
	</div>
</div>
