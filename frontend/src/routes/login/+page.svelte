<script lang="ts">
	import { page } from '$app/stores';

	const setTournamentId = () => {
		if ($page.url.searchParams.get('tournament_id'))
			return $page.url.searchParams.get('tournament_id');
		return '';
	};

	const disableIdField = () => {
		if ($page.url.searchParams.get('tournament_id')) return true;
		return false;
	};

	let searching = true;
	let fencerFound = false;
	let fencerName: string;
	let fencerId: string;
	let tournamentId: string;

	if ($page.url.searchParams.get('tournament_id')) {
		tournamentId = $page.url.searchParams.get('tournament_id');
	}
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<div class="w-full h-screen flex justify-center items-center bg-slate-200">
	<div class="card w-96 bg-base-100 shadow-xl m-4">
		<div class="card-body">
			<div class="card-title">Fencer Login</div>
			<form
				class="flex flex-col gap-2 my-5"
				on:submit={(e) => {
					e.preventDefault();
					login_modal.showModal();
					const prefix = 'http://127.0.0.1:8080';
					fetch(prefix + '/login-fencer', {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({
							tournament_id: e.target[0].value,
							search: e.target[1].value
						})
					})
						.then((res) => res.json())
						.then((data) => {
							searching = false;
							if (data.success == "Fencer found") {
								fencerFound = true;
								fencerName = data.description;
								tournamentId = data.tournament_id;
								fencerId = data.fencer_id;
							} else {
								fencerFound = false;
								console.error(data)
							}
						})
						.catch((err) => {
							console.error(err);
							searching = false;
							fencerFound = false;
						});
				}}
			>
				<input
					type="text"
					placeholder="Tournament ID"
					class="input input-bordered w-full max-w-xs"
					value={setTournamentId()}
					disabled={disableIdField()}
				/>
				<input
					type="text"
					placeholder="Name or Number"
					class="input input-bordered w-full max-w-xs"
				/>
				<button type="submit" class="btn btn-primary">Login</button>
			</form>
			<a href="/QWCO0Z/1DMHDUNLHI" class="btn btn-secondary">Login</a>
		</div>
	</div>
</div>
<dialog id="login_modal" class="modal">
	<form method="dialog" class="modal-box text-center">
		{#if searching}
			<div class="flex justify-center align-center">
				<i class="fa-solid fa-circle-notch fa-spin text-2xl" />
			</div>
		{:else if fencerFound}
			<i class="fa-solid fa-check-circle text-2xl mb-3 text-success" />
			<h3 class="font-bold text-lg">Fencer Found</h3>
			<p>{fencerName}</p>
		{:else}
			<i class="fa-solid fa-xmark-circle text-3xl mb-3 text-error" />
			<h3 class="font-bold text-lg">Fencer Not Found</h3>
			<p>An Error Occured. Please try again or contact the Tournament Office</p>
		{/if}
		<div class="modal-action">
			{#if !searching}
				<button class="btn">Close</button>
				{#if fencerFound}
					<a href={`/${tournamentId}/${fencerId}`} class="btn btn-success">Login</a>
				{/if}
			{/if}
		</div>
	</form>
</dialog>
