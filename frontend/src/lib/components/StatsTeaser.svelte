<script lang="ts">
	import { page } from '$app/stores';
	import { userData } from '$lib/stores';
	import { fly } from 'svelte/transition';
</script>

<div class="w-full flex flex-col gap-6 md:flex-row justify-center align-center">
	<div class="stats stats-vertical sm:stats-horizontal shadow-lg" in:fly={{ y: 50, duration: 500, delay: 200 }}>
		<div class="stat place-items-center">
			<div class="stat-title">Overall Rank</div>
			<div class="stat-value text-primary">{$userData.current_rank}</div>
		</div>
		{#if $userData.current_group_rank}
			<div class="flex-1 stat place-items-center">
				<div class="stat-title">Group Rank</div>
				<div class="stat-value">{$userData.current_group_rank}</div>
			</div>
		{/if}
	</div>

	<div class="stats stats-vertical sm:stats-horizontal shadow-lg" in:fly={{ y: 50, duration: 500, delay: 300 }}>
		<div class="stat place-items-center">
			<div class="stat-title">Win Rate</div>
			<div class="stat-value">{$userData.win_percentage}%</div>
		</div>
		<div class="stat place-items-center">
			<div class="stat-title">Point Difference</div>
			<div class="stat-value">{$userData.points_difference}</div>
		</div>
	</div>
</div>
