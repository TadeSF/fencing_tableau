<script lang="ts">
  import RankingHistoryChart from '$lib/components/RankingHistoryChart.svelte';

	import { onMount } from 'svelte';
	import { pageTitle } from '$lib/stores';
	import { userData } from '$lib/stores';
	import ChartCard from '$lib/components/ChartCard.svelte';
	import PDOverTimeChart from '$lib/components/PDOverTimeChart.svelte';
	import PDPerMatch from '$lib/components/PDPerMatch.svelte';

	pageTitle.set('Statistics');
</script>

<div class="w-full flex justify-center align-center">
	<div class="m-4 w-full flex flex-row gap-4 flex-wrap justify-center items-center">
		<div class="flex w-full flex-col justify-center items-center">
			<h2 class="text-xl font-bold text-center">Match Statistics</h2>
		</div>
		<div class="stats stats-vertical w-full sm:w-auto sm:stats-horizontal shadow-xl bg-white">
			<div class="stat place-items-center">
				<div class="stat-title">Matches</div>
				<div class="stat-value text-primary">{$userData.statistics.overall.matches}</div>
			</div>

			<div class="stat place-items-center">
				<div class="stat-title">Victories</div>
				<div class="stat-value text-secondary">{$userData.statistics.overall.wins}</div>
			</div>

			<div class="stat place-items-center">
				<div class="stat-title">Defeats</div>
				<div class="stat-value text-secondary">{$userData.statistics.overall.losses}</div>
			</div>

			<div class="stat place-items-center">
				<div
					class="radial-progress border-4"
					style={`--value:${$userData.win_percentage}; --thickness: 0.8rem`}
				>
					{$userData.win_percentage}%
				</div>
			</div>
		</div>

		<div class="flex w-full flex-col justify-center items-center mt-10">
			<h2 class="text-xl font-bold text-center">Point Statistics</h2>
		</div>
		<div class="stats stats-vertical w-full sm:w-auto sm:stats-horizontal shadow-xl bg-white">
			<div class="stat place-items-center">
				<div class="stat-title">For</div>
				<div class="stat-value text-primary">{$userData.statistics.overall.points_for}</div>
			</div>

			<div class="stat place-items-center">
				<div class="stat-title">Against</div>
				<div class="stat-value text-secondary">{$userData.statistics.overall.points_against}</div>
			</div>

			<div class="stat place-items-center">
				<div class="stat-title">Difference</div>
				<div class="stat-value text-secondary">{$userData.points_difference}</div>
			</div>

			<div class="stat place-items-center">
				<div class="stat-title">per Match</div>
				<div class="stat-value">{$userData.points_per_match}</div>
			</div>
		</div>

		<div class="flex w-full flex-col justify-center items-center mt-10">
			<h2 class="text-xl font-bold text-center">Graphs</h2>
		</div>
        <ChartCard title="Ranking History">
            <RankingHistoryChart />
        </ChartCard>
        <ChartCard title="Point Difference over Time">
            <PDOverTimeChart />
        </ChartCard>
        <ChartCard title="Point Difference per Match">
            <PDPerMatch />
        </ChartCard>
	</div>
</div>
