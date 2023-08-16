<script lang="ts">
	import AvatarFlag from './AvatarFlag.svelte';

	import { page } from '$app/stores';
	import { userData } from '$lib/stores';
	import { fly, fade } from 'svelte/transition';

	export let showDetailsButton = false;
	export let showToggleButton = false;

	let prefix = 'http://127.0.0.1:8080';

	$: activeMatchStatus = (() => {
		if (!$userData.next_matches[0]) return { color: '', icon: 'fa-bug', shake: false };
		else if ($userData.next_matches[0].ongoing == true)
			return {
				color: '',
				icon: 'fa-spin fa-spinner-third',
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
				icon: 'fa-bell-exclamation',
				shake: false
			};
		else if ($userData.next_matches[0].piste == 'TBA')
			return {
				color: '',
				icon: 'fa-user-clock',
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
				<div class="stats stats-vertical lg:stats-horizontal">
					<div class={`stat place-items-center`}>
						<div class="stat-title">Status</div>
						<div class="stat-value">
							<i
								class={`fa-solid ${activeMatchStatus.icon} text-3xl ${
									activeMatchStatus.shake && 'fa-shake'
								} ${activeMatchStatus.color}`}
							/>
						</div>
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Piste</div>
						{#if $userData.next_matches[0].piste == 'TBA'}
							<div class="stat-value">
								<i class="fas fa-location-dot-slash text-3xl text-slate-400" />
							</div>
						{:else}
							<div class="stat-value">{$userData.next_matches[0].piste}</div>
						{/if}
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Side</div>
						<div class="stat-value">
							<i
								class={`fa-solid ${
									$userData.next_matches[0].color != null
										? $userData.next_matches[0].color == 'green'
											? 'fa-square-arrow-right'
											: 'fa-square-arrow-left'
										: 'fa-bug'
								} ${$userData.next_matches[0].color}
								${$userData.next_matches[0].color == 'green' && 'text-green-600'} ${
									$userData.next_matches[0].color == 'red' && 'text-red-600'
								} ${$userData.next_matches[0].color == '' && 'text-slate-400'}
								text-3xl`}
							/>
						</div>
					</div>
					<div class="stat place-items-center">
						<div class="stat-title">Opponent</div>
						<div class="stat-value flex flex-col sm:flex-row gap-2 justify-center items-center">
							<AvatarFlag flag={$userData.next_matches[0].opponent.nationality} size="w-10" />
							<div class="btn btn-ghost h-fit justify-self-end text-2xl">
								{$userData.next_matches[0].opponent.name}
							</div>
						</div>
					</div>
					{#if $userData.allow_fencers_to_input_scores || $userData.allow_fencers_to_start_matches}
						<div class="stat place-items-center">
							<div class="stat-title">Options</div>
							{#if !$userData.next_matches[0].ongoing && $userData.allow_fencers_to_start_matches}
								<div class="stat-value">
									<button
										class="btn btn-accent"
										on:click={() => {
											fetch(
												`${prefix}/api/matches/set-active?tournament_id=${$page.params.tournament}&match_id=${$userData.next_matches[0].id}`,
												{
													method: 'POST',
													headers: { 'Content-Type': 'application/json' },
													body: JSON.stringify({
														override_flag: false
													})
												}
											).catch((err) => {
												console.error(err);
											});
										}}
										disabled={$userData.next_matches[0].ongoing ||
											$userData.next_matches[0].piste_occupied ||
											$userData.next_matches[0].piste == 'TBA'}
									>
										<i class="fa-solid fa-circle-play" />
										<span class="ml-2">Start Match</span>
									</button>
								</div>
							{:else if $userData.next_matches[0].ongoing && $userData.allow_fencers_to_input_scores}
								<div class="stat-value">
									<button
										class="btn btn-secondary"
										on:click={() => {
											input_score_modal.showModal();
										}}
										disabled={!$userData.next_matches[0].ongoing}
									>
										<i class="fa-solid fa-pen-to-square" />
										<span class="ml-2">Input Score</span>
									</button>
								</div>
							{/if}
						</div>
					{/if}
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
		{/if}
	</div>
</div>
{#if $userData.allow_fencers_to_input_scores && $userData.next_matches}
	<dialog id="input_score_modal" class="modal">
		<form
			method="dialog"
			class="modal-box flex flex-col sm:flex-row gap-3"
			on:submit={(e) => {
				fetch(
					`${prefix}/api/matches/push-score?tournament_id=${$page.params.tournament}&match_id=${$userData.next_matches[0].id}`,
					{
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({
							red_score: e.target[0].value,
							green_score: e.target[1].value
						})
					}
				).catch((err) => {
					console.error(err);
				});

				// clear the form
				e.target[0].value = '';
				e.target[1].value = '';
			}}
		>
			<input
				type="text"
				placeholder={$userData.next_matches[0]?.color != 'red'
					? $userData.next_matches[0]?.opponent.name
					: $userData.name}
				class="input input-bordered bg-red-500 text-white placeholder:text-red-300 w-full"
				required
			/>

			<input
				type="text"
				placeholder={$userData.next_matches[0]?.color != 'green'
					? $userData.next_matches[0]?.opponent.name
					: $userData.name}
				class="input input-bordered bg-green-600 text-white placeholder:text-green-300 w-full"
				required
			/>
			<button class="btn btn-accent" type="submit">submit</button>
		</form>
		<form method="dialog" class="modal-backdrop">
			<button>close</button>
		</form>
	</dialog>
{/if}

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
