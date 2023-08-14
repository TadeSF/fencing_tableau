<script lang="ts">
	import AvatarFlag from './AvatarFlag.svelte';

	import { page } from '$app/stores';
	import { userData } from '$lib/stores';
	import { fly, fade } from 'svelte/transition';

	export let showDetailsButton = false;
	export let showToggleButton = false;
	let drawerIsOpen = false;

	$: activeMatchColor = (() => {
		if (!$userData.next_matches[0]) return { color: '', icon: faBug, shake: false };
		else if ($userData.next_matches[0].ongoing == true)
			return {
				color: '',
				icon: "fa-spin fa-circle-notch",
				shake: false
			};
		else if (
			$userData.next_matches[0].piste_occupied == false &&
			$userData.next_matches[0].ongoing == false
		)
			return {
				color: 'text-error',
				icon: 'fa-bell',
				shake: true
			};
		else if (
			$userData.next_matches[0].piste_occupied == true &&
			$userData.next_matches[0].ongoing == false
		)
			return {
				color: 'text-warning',
				icon: 'fa-bell',
				shake: false
			};
		else if ($userData.next_matches[0].piste == 'TBA')
			return {
				color: '',
				icon: 'fa-clock',
				shake: false
			};
		else {
			console.error(
				$userData.next_matches[0].piste,
				$userData.next_matches[0].ongoing,
				$userData.next_matches[0].piste_occupied
			);
			return {
				color: '',
				icon: 'fa-bug',
				shake: false
			};
		}
	})();
</script>

<div class="w-full flex justify-center align-center">
	<div
		class="w-full sm:w-auto h-fit card bg-slate-50 flex flex-col justify-center align-center shadow-lg p-4"
		in:fly={{ y: 50, duration: 500 }}
	>
		{#if !$userData.next_matches}
			<div
				class="flex flex-col sm:flex-row gap-4 justify-center items-center"
				in:fade={{ delay: 1000 }}
				out:fade
			>
				<i class="fa-solid fa-warning text-xl text-warning" />
				<h1 class="text-xl font-bold">No matches Found</h1>
			</div>
			{:else if $userData.next_matches.length === 0}
			<div
			class="flex flex-col sm:flex-row gap-4 justify-center items-center"
			in:fade={{ delay: 1000 }}
			out:fade
			>
			
				<i class="fa-solid fa-check-circle text-xl text-success" />
				<h1 class="text-xl font-bold">All matches finished in this stage.</h1>
			</div>
		{:else}
			<div in:fade={{ delay: 1000 }} out:fade class="flex flex-col sm:flex-row gap-10">
				<div class="stats stats-vertical sm:stats-horizontal">
					<div class={`stat place-items-center`}>
						<div class="stat-title">Status</div>
						<div class="stat-value">
							<i class={`fa-solid ${activeMatchColor.icon} text-3xl ${activeMatchColor.shake && 'fa-shake'} ${activeMatchColor.color}`} />
						</div>
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Piste</div>
						<div class="stat-value">{$userData.next_matches[0].piste}</div>
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Side</div>
						<div class="stat-value">
							<div class={`${$userData.next_matches[0].color == "green" && "bg-green-600"} ${$userData.next_matches[0].color == "red" && "bg-red-600"} ${$userData.next_matches[0].color == "" && "bg-slate-200"} w-10 h-10 rounded-full`}></div>
						</div>
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Opponent</div>
						<div
							class="stat-value flex flex-col sm:flex-row gap-2 justify-center items-center"
						>
							<AvatarFlag flag={$userData.next_matches[0].opponent.nationality} size="w-10" />
							<div class="btn btn-ghost h-fit justify-self-end text-2xl">
								{$userData.next_matches[0].opponent.name}
							</div>
						</div>
					</div>
					{#if showDetailsButton}
						<a class="stat place-items-center" href={`${$page.url.pathname}/matches`}>
							<div class="stat-title">Details</div>
							<div class="stat-value btn btn-ghost">
								<i class="fa-solid fa-up-right-from-square text-xl" />
							</div>
						</a>
					{/if}
				</div>
			</div>
			{#if showToggleButton}
				<div
					class={`${
						drawerIsOpen ? 'h-auto' : 'h-0 hidden'
					} flex flex-col justify-center items-center mt-5`}
				>
					<slot />
				</div>
			{/if}
		{/if}
	</div>
</div>

<style lang="scss">
	.stat-value {
		min-height: 60px;
		display: flex;
		align-items: center;
		justify-content: center;
		
		.btn {
			text-transform: none;
		}

	}
</style>